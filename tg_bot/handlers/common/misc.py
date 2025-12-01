from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message

private_router = Router()
group_router = Router()
global_router = Router()


@global_router.message(Command("ping"))
async def cmd_ping(message: Message):
    await message.answer("pong")

