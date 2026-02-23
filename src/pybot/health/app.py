from __future__ import annotations

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from dishka.integrations.fastapi import DishkaRoute, FromDishka, setup_dishka
from fastapi import FastAPI, Query
from fastapi.responses import JSONResponse

from ..core import logger
from ..di.containers import setup_health_container
from ..dto.health_dto import HealthStatusDTO
from ..services.health import HealthService

container = setup_health_container()


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    logger.info("Health API started")
    try:
        yield
    finally:
        await app.state.dishka_container.close()
        logger.info("Health API stopped")


app = FastAPI(title="ITAcadem Health API", docs_url="/docs", redoc_url="/redocs", lifespan=lifespan)
app.router.route_class = DishkaRoute
setup_dishka(container=container, app=app)


@app.get(
    "/health",
    response_model=HealthStatusDTO,
    response_model_exclude_none=True,
    tags=["health"],
    summary="Liveness probe",
    description="Returns OK if the process is running. No external dependencies are checked.",
    responses={
        200: {
            "description": "Process is alive.",
        },
    },
)
async def health(health_service: FromDishka[HealthService]) -> HealthStatusDTO:
    """Return liveness status of the process.

    Args:
        health_service: Health application service resolved from Dishka container.

    Returns:
        HealthStatusDTO: Liveness status payload.
    """
    return await health_service.health()


@app.get(
    "/ready",
    response_model=HealthStatusDTO,
    response_model_exclude_none=True,
    tags=["health"],
    summary="Readiness probe",
    description="Checks database connectivity with a short SELECT 1 query. Returns 200 if OK, 503 otherwise.",
    responses={
        200: {
            "description": "Service is ready to serve traffic.",
        },
        503: {
            "description": "Service is not ready (database is unavailable).",
            "model": HealthStatusDTO,
        },
    },
)
async def ready(
    health_service: FromDishka[HealthService],
    include_checks: bool = Query(
        default=True,
        description="Включать список проверок в ответ.",
    ),
) -> JSONResponse | HealthStatusDTO:
    """Return readiness status based on database connectivity.

    Args:
        health_service: Health application service resolved from Dishka container.
        include_checks: If False, return status without checks list.

    Returns:
        HealthStatusDTO | JSONResponse: Readiness payload or 503 response on failure.
    """
    status_dto, is_ready = await health_service.ready()
    if not include_checks:
        status_dto = status_dto.model_copy(update={"checks": []})
    if is_ready:
        return status_dto
    return JSONResponse(status_code=503, content=status_dto.model_dump(mode="json"))
