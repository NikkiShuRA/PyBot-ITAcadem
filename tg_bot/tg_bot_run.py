from aiogram import Bot, Dispatcher
from aiogram.types import Update
from aiogram import F
from aiogram_dialog import setup_dialogs

from config import BOT_TOKEN
from db_class.database import SessionLocal, init_db

from tg_bot.handlers.common import common_router 

# диалоги и роутеры модуля user
from tg_bot.handlers.user import user_router


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

    # Подключаем остальные роутеры common
    dp.include_router(common_router)

    # Подключаем остальные роутеры user
    dp.include_router(user_router)

    # Инициализируем DialogManager для работы с диалогами
    setup_dialogs(dp)

    # сбросить накопившиеся апдейты
    await bot.delete_webhook(drop_pending_updates=True)

    print("Запуск бота")
    await dp.start_polling(bot)
