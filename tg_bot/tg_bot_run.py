from aiogram import Bot, Dispatcher
from aiogram.types import Update
from aiogram import F
from aiogram_dialog import setup_dialogs

from config import BOT_TOKEN
from db_class.database import SessionLocal, init_db

from tg_bot.handlers.common import private_router as common_private_router
from tg_bot.handlers.common import group_router as common_group_router
from tg_bot.handlers.common import global_router as common_global_router

# диалоги и роутеры модуля user
from tg_bot.handlers.user import user_dialogs
from tg_bot.handlers.user import private_router as user_private_router
from tg_bot.handlers.user import group_router as user_group_router
from tg_bot.handlers.user import global_router as user_global_router


# простейший middleware для сессии БД
from aiogram import BaseMiddleware
from typing import Callable, Awaitable, Dict, Any


class DbSessionMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[Update, Dict[str, Any]], Awaitable[Any]],
        event: Update,
        data: Dict[str, Any],
    ) -> Any:
        async with SessionLocal() as session:
            data["db"] = session
            return await handler(event, data)


async def tg_bot_main():
    await init_db()

    bot = Bot(BOT_TOKEN)
    dp = Dispatcher()
    dp.message.middleware(DbSessionMiddleware())

    # Подключаем диалоги
    dp.include_router(user_dialogs)

    # Подключаем остальные роутеры common
    dp.include_router(common_global_router)
    dp.include_router(common_private_router)
    dp.include_router(common_group_router)

    # Подключаем остальные роутеры user
    dp.include_router(user_global_router)
    dp.include_router(user_private_router)
    dp.include_router(user_group_router)

    # Инициализируем DialogManager для работы с диалогами
    setup_dialogs(dp)

    # сбросить накопившиеся апдейты
    await bot.delete_webhook(drop_pending_updates=True)

    print("Запуск бота")
    await dp.start_polling(bot)
