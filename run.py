from aiorun import run

from src.pybot.bot.tg_bot_run import tg_bot_main
from src.pybot.core import logger

if __name__ == "__main__":
    try:
        run(tg_bot_main(), shutdown_callback=lambda loop: logger.info("Бот остановлен"))
    finally:
        logger.complete()
