from aiogram import Bot, Dispatcher
from aiogram.types import Update
from aiogram import F

from config import BOT_TOKEN
from db_class.database import SessionLocal, init_db

# тестовый роутер
from tg_bot.handlers.test import router 

# роутеры модуля common
from tg_bot.handlers.common import private_router as common_private_router
from tg_bot.handlers.common import group_router as common_group_router
from tg_bot.handlers.common import global_router as common_global_router


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

    # Подключаем роутеры common
    dp.include_router(common_global_router)
    dp.include_router(common_private_router)
    dp.include_router(common_group_router)

    # сбросить накопившиеся апдейты
    await bot.delete_webhook(drop_pending_updates=True)

    print("Запуск бота")
    await dp.start_polling(bot)
