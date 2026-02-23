from __future__ import annotations

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from dishka.integrations.fastapi import DishkaRoute, FromDishka, setup_dishka
from fastapi import FastAPI
from fastapi.responses import JSONResponse

from ..core import logger
from ..di.containers import setup_health_container
from ..dto.health_dto import HealthStatusDTO
from ..services.health import HealthService


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    logger.info("Health API started")
    try:
        yield
    finally:
        container = app.state.health_container
        await container.close()
        logger.info("Health API stopped")


def create_app() -> FastAPI:
    app = FastAPI(title="ITAcadem Health API", docs_url="/docs", redoc_url=None, lifespan=lifespan)
    app.router.route_class = DishkaRoute

    container = setup_health_container()
    setup_dishka(container, app)
    app.state.health_container = container

    app.get("/health", response_model=HealthStatusDTO)(health)
    app.get(
        "/ready",
        response_model=HealthStatusDTO,
        responses={503: {"model": HealthStatusDTO}},
    )(ready)

    return app


async def health(health_service: FromDishka[HealthService]) -> HealthStatusDTO:
    return await health_service.health()


async def ready(health_service: FromDishka[HealthService]) -> JSONResponse | HealthStatusDTO:
    status_dto, is_ready = await health_service.ready()
    if is_ready:
        return status_dto
    return JSONResponse(status_code=503, content=status_dto.model_dump(mode="json"))
