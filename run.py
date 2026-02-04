import asyncio

from src.pybot.bot.tg_bot_run import tg_bot_main
from src.pybot.core import logger

if __name__ == "__main__":
    try:
        asyncio.run(tg_bot_main())
    finally:
        logger.complete()
