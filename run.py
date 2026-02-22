import asyncio
import logging
import multiprocessing

from src.pybot.admin.app import run_admin
from src.pybot.bot.tg_bot_run import tg_bot_main

logger = logging.getLogger(__name__)


def run_fastapi() -> None:
    """FastAPI admin panel process."""
    run_admin()


def run_telegram_bot() -> None:
    """Telegram bot process."""
    asyncio.run(tg_bot_main())


if __name__ == "__main__":
    # Создание процессов
    fastapi_process = multiprocessing.Process(target=run_fastapi)
    bot_process = multiprocessing.Process(target=run_telegram_bot)

    # Запуск процессов
    fastapi_process.start()
    bot_process.start()

    logger.info("✅ Both processes started!")

    # Ожидаем завершения
    try:
        fastapi_process.join()
        bot_process.join()
    except KeyboardInterrupt:
        logger.info("🛑 Shutting down...")
        fastapi_process.terminate()
        bot_process.terminate()
        fastapi_process.join()
        bot_process.join()
        logger.info("✅ All processes stopped.")
