from aiogram.filters import Command
from aiogram.types import Message

from ...filters import create_chat_type_routers

_, _, misc_global_router = create_chat_type_routers("start")


@misc_global_router.message(Command("ping"))
async def cmd_ping(message: Message) -> None:
    await message.answer("pong")
