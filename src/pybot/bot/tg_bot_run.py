from aiogram import Bot, Dispatcher
from aiogram_dialog import setup_dialogs
from yaspin import yaspin

from ..core import logger
from ..core.config import settings
from ..db.database import SessionLocal
from .dialogs import user_router
from .handlers import (
    common_router,
    points_router,
    profile_router,  # !!! Костыль вывода профиля (Нужно перепроверить и улучшить)
)
from .middlewares import DbSessionMiddleware


async def tg_bot_main() -> None:
    with yaspin(text="Инициализация бота...", color="cyan") as sp:
        bot = Bot(settings.bot_token_test)
        dp = Dispatcher()
        dp.update.middleware(DbSessionMiddleware(SessionLocal))

        # Подключаем остальные роутеры common
        dp.include_router(common_router)
        dp.include_router(points_router)
        dp.include_router(profile_router)  # !!! Костыль вывода профиля (Нужно перепроверить и улучшить)
        dp.include_router(user_router)

        # Инициализируем DialogManager для работы с диалогами
        setup_dialogs(dp)

        # сбросить накопившиеся апдейты
        await bot.delete_webhook(drop_pending_updates=True)

        logger.info("Запуск бота")
        sp.ok("✅ Бот запущен!")
    await dp.start_polling(bot)
