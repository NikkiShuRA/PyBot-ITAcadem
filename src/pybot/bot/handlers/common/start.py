from aiogram import flags
from aiogram.filters import Command, CommandStart
from aiogram.types import Message
from aiogram_dialog import DialogManager
from aiogram_dialog.api.entities.modes import StartMode
from dishka.integrations.aiogram import FromDishka
from sqlalchemy.ext.asyncio import AsyncSession

from ....bot.dialogs.user_reg.states import CreateProfileSG
from ....services.users import UserService
from ...filters import create_chat_type_routers
from ...keyboards.auth import request_contact_kb
from ...texts import HELP_GROUP, HELP_PRIVATE, INFO_GLOBAL
from ..profile.grand_profile import show_profile

start_private_router, start_group_router, start_global_router = create_chat_type_routers("start")


# /start - в личном чате
@start_private_router.message(CommandStart())
@flags.public(True)
async def cmd_start_private(
    message: Message,
    dialog_manager: DialogManager,
    user_service: FromDishka[UserService],
    db: FromDishka[AsyncSession],
) -> None:
    if not message.from_user:
        await message.answer("Ошибка обработки пользователя.")
        return

    user = await user_service.get_user_by_telegram_id(message.from_user.id)  # UserReadDTO | None

    if user:
        await show_profile(message, db, user)
        return
    else:
        await message.answer(
            "Пожалуйста, отправьте свой контакт, используя кнопку ниже.", reply_markup=request_contact_kb
        )
        await dialog_manager.start(CreateProfileSG.contact, mode=StartMode.RESET_STACK)


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
