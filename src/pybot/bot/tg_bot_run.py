from collections.abc import Awaitable, Callable
from typing import Any

# простейший middleware для сессии БД
from aiogram import BaseMiddleware, Bot, Dispatcher
from aiogram.types import TelegramObject, Update
from aiogram_dialog import setup_dialogs
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker
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


class DbSessionMiddleware(BaseMiddleware):
    def __init__(self, session_maker: async_sessionmaker[AsyncSession]) -> None:
        super().__init__()
        self.session_maker = session_maker

    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: dict[str, Any],
    ) -> Any:
        if not isinstance(event, Update):
            return await handler(event, data)

        async with self.session_maker() as session:
            data["db"] = session
            return await handler(event, data)


async def tg_bot_main() -> None:
    with yaspin(text="Инициализация бота...", color="cyan") as sp:
        bot = Bot(settings.bot_token_test)
        dp = Dispatcher()
        dp.update.middleware(DbSessionMiddleware(SessionLocal))

        # Подключаем остальные роутеры common
        dp.include_router(common_router)
        dp.include_router(points_router)
        dp.include_router(profile_router)                                           # !!! Костыль вывода профиля (Нужно перепроверить и улучшить)
        dp.include_router(user_router)
        
        # Инициализируем DialogManager для работы с диалогами
        setup_dialogs(dp)

        # сбросить накопившиеся апдейты
        await bot.delete_webhook(drop_pending_updates=True)

        logger.info("Запуск бота")
        sp.ok("✅ Бот запущен!")
    await dp.start_polling(bot)
