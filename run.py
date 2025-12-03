import asyncio

from .src.pybot.bot.tg_bot_run import tg_bot_main

if __name__ == "__main__":
    asyncio.run(tg_bot_main())
