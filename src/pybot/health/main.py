from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from dishka.integrations.fastapi import DishkaRoute, setup_dishka
from fastapi import FastAPI

from ..core import logger
from ..di.containers import setup_health_container
from .routers import health, readiness


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    logger.info("Health API started")
    try:
        yield
    finally:
        dishka_container = getattr(app.state, "dishka_container", None)
        if dishka_container is not None:
            await dishka_container.close()
        logger.info("Health API stopped")


def create_app() -> FastAPI:
    app = FastAPI(title="ITAcadem Health API", docs_url="/docs", redoc_url="/redocs", lifespan=lifespan)
    app.router.route_class = DishkaRoute
    app.include_router(readiness.router)
    app.include_router(health.router)
    setup_dishka(container=setup_health_container(), app=app)
    return app


app = create_app()
