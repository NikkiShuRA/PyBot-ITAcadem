from aiogram.filters import Command, CommandStart
from aiogram.types import Message
from aiogram_dialog import DialogManager
from sqlalchemy.ext.asyncio import AsyncSession

from ...filters import create_chat_type_routers
from ...texts import (
    HELP_GROUP,
    HELP_PRIVATE,
    INFO_GLOBAL,
)
from ..profile.grand_profile import cmd_profile_private

start_private_router, start_group_router, start_global_router = create_chat_type_routers("start")


# /start - в личном чате
@start_private_router.message(CommandStart())
async def cmd_start_private(message: Message, dialog_manager: DialogManager, db: AsyncSession) -> None:
    await cmd_profile_private(message, dialog_manager, db)


# /start - в групповом чате
@start_global_router.message(CommandStart())
async def cmd_start_group(message: Message) -> None:
    await message.answer("Всем привет!")


# /info - в личном/групповом чате
@start_global_router.message(Command("info"))
async def cmd_info(message: Message) -> None:
    await message.answer(INFO_GLOBAL)


# /help - в личномчате
@start_private_router.message(Command("help"))
async def cmd_help_private(message: Message) -> None:
    await message.answer(HELP_PRIVATE)


# /help - в групповом чате
@start_group_router.message(Command("help"))
async def cmd_help_group(message: Message) -> None:
    await message.answer(HELP_GROUP)
