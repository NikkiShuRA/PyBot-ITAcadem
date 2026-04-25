"""Readiness probe router for Health API.

This module provides the /ready endpoint to check if the application dependencies,
such as the database, are available and ready to serve traffic.
"""

from dishka.integrations.fastapi import DishkaRoute, FromDishka
from fastapi import APIRouter, Query
from fastapi.responses import JSONResponse

from .....dto.health_dto import HealthStatusDTO
from .....services.health import HealthService

router = APIRouter(route_class=DishkaRoute)


@router.get(
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
        description="Include dependency checks in the response.",
    ),
) -> JSONResponse | HealthStatusDTO:
    """Return readiness status based on database connectivity.

    Args:
        health_service (HealthService): Health application service resolved from Dishka container.
        include_checks (bool): If False, return status without checks list. Defaults to True.

    Returns:
        HealthStatusDTO | JSONResponse: Readiness payload or 503 response on failure.
    """
    status_dto, is_ready = await health_service.ready()
    if not include_checks:
        status_dto = status_dto.model_copy(update={"checks": []})
    if is_ready:
        return status_dto
    return JSONResponse(status_code=503, content=status_dto.model_dump(mode="json"))
