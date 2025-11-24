from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message

private_router = Router()
group_router = Router()
global_router = Router()


@global_router.message(Command("ping"))
async def cmd_ping(message: Message):
    await message.answer("pong")


# Простейший echo-хендлер по желанию (можно отключить в проде)
@global_router.message(F.text & ~F.text.startswith("/"))
async def echo_text(message: Message):
    # тут можно поставить DEBUG-флаг и включать только в dev
    await message.answer(message.text)
