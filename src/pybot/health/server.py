from __future__ import annotations

import asyncio
from contextlib import suppress
from multiprocessing.synchronize import Event as MpEvent

import uvicorn

from ..core import logger
from ..core.config import settings


async def _watch_stop(server: uvicorn.Server, stop_event: MpEvent) -> None:
    while not stop_event.is_set():
        await asyncio.sleep(0.2)
    server.should_exit = True


def run_health_server(stop_event: MpEvent) -> None:
    config = uvicorn.Config(
        "src.pybot.health.app:app",
        host=settings.health_api_host,
        port=settings.health_api_port,
        log_level=settings.log_level.lower(),
        access_log=False,
    )
    server = uvicorn.Server(config)

    async def _serve() -> None:
        watcher = asyncio.create_task(_watch_stop(server, stop_event))
        try:
            await server.serve()
        finally:
            watcher.cancel()
            with suppress(asyncio.CancelledError):
                await watcher

    logger.info(
        "Health API process starting on http://{host}:{port}",
        host=settings.health_api_host,
        port=settings.health_api_port,
    )
    asyncio.run(_serve())
