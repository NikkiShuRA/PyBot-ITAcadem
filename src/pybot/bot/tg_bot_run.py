from collections.abc import Awaitable, Callable
from typing import Any

# простейший middleware для сессии БД
from aiogram import BaseMiddleware, Bot, Dispatcher
from aiogram.types import Update
from aiogram_dialog import setup_dialogs

from ..bot.handlers.common import common_router
from ..core import logger
from ..core.config import settings
from ..db.database import SessionLocal, init_db
from .handlers import global_router, group_router, private_router

# common_router = Router()
# common_router.include_routers(private_router, group_router, global_router)

# Роутер для личных чатов
# private_router = Router()
# private_router.message.filter(F.chat.type == "private")

# # Роутер для групп/супергрупп
# group_router = Router()
# group_router.message.filter(F.chat.type.in_({"group", "supergroup"}))

# # Роутер для всех типов чатов
# global_router = Router()
# global_router.message.filter(F.chat.type.in_({"private", "group", "supergroup"}))

# common_router = Router()
# common_router.include_routers(private_router, group_router, global_router)


class DbSessionMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[Update, dict[str, Any]], Awaitable[Any]],
        event: Update,
        data: dict[str, Any],
    ) -> Any:
        async with SessionLocal() as session:
            data["db"] = session
            return await handler(event, data)


async def tg_bot_main() -> None:
    await init_db()

    bot = Bot(settings.bot_token)
    dp = Dispatcher()
    dp.message.middleware(DbSessionMiddleware())

    dp.include_router(private_router)
    dp.include_router(group_router)
    dp.include_router(global_router)
    # Подключаем остальные роутеры common
    # dp.include_router(common_router)

    # Инициализируем DialogManager для работы с диалогами
    setup_dialogs(dp)

    # сбросить накопившиеся апдейты
    await bot.delete_webhook(drop_pending_updates=True)

    logger.info("Запуск бота")
    await dp.start_polling(bot)
