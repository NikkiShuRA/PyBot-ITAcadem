import asyncio
import multiprocessing as mp
from multiprocessing.process import BaseProcess
from multiprocessing.synchronize import Event as MpEvent

from src.pybot.bot.tg_bot_run import tg_bot_main
from src.pybot.core import logger
from src.pybot.core.config import settings
from src.pybot.health.server import run_health_server

if __name__ == "__main__":
    health_process: BaseProcess | None = None
    stop_event: MpEvent | None = None

    if settings.health_api_enabled:
        ctx = mp.get_context("spawn")
        stop_event = ctx.Event()
        process = ctx.Process(
            target=run_health_server,
            args=(stop_event,),
            name="health-api",
        )
        process.start()
        health_process = process
        logger.info("Health API process started (pid={pid})", pid=process.pid)
    else:
        logger.info("Health API process disabled by HEALTH_API_ENABLED")

    try:
        asyncio.run(tg_bot_main())
    finally:
        if health_process and stop_event:
            stop_event.set()
            health_process.join(timeout=5)
            if health_process.is_alive():
                logger.warning("Health API did not stop gracefully, terminating...")
                health_process.terminate()
                health_process.join(timeout=5)
