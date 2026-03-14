from aiogram import flags
from aiogram.filters import Command, CommandStart
from aiogram.types import Message
from aiogram_dialog import DialogManager
from aiogram_dialog.api.entities.modes import StartMode
from dishka.integrations.aiogram import FromDishka

from ....bot.dialogs.user_reg.states import CreateProfileSG
from ....services import UserProfileService
from ....services.users import UserService
from ...filters import create_chat_type_routers
from ...texts import HELP_GROUP, HELP_PRIVATE, INFO_GLOBAL

start_private_router, start_group_router, start_global_router = create_chat_type_routers("start")


# /start - в личном чате
@start_private_router.message(CommandStart())
@flags.public(True)
async def cmd_start_private(
    message: Message,
    dialog_manager: DialogManager,
    user_service: FromDishka[UserService],
    user_profile_service: FromDishka[UserProfileService],
) -> None:
    if not message.from_user:
        await message.answer("Ошибка обработки пользователя.")
        return

    user = await user_service.find_user_by_telegram_id(message.from_user.id)  # UserReadDTO | None

    if user:
        await user_profile_service.manage_profile(user)
        return

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
