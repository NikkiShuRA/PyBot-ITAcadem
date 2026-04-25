"""Stable public API for the web presentation layer."""

from .health import main as main
from .health.main import app, create_app, lifespan
from .health.routers.health import health as health_endpoint
from .health.routers.health import router as health_router
from .health.routers.readiness import ready as ready_endpoint
from .health.routers.readiness import router as readiness_router

__all__ = [
    "app",
    "create_app",
    "health_endpoint",
    "health_router",
    "lifespan",
    "main",
    "readiness_router",
    "ready_endpoint",
]
