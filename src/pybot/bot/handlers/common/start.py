from aiogram import flags
from aiogram.filters import Command, CommandStart
from aiogram.types import Message
from aiogram_dialog import DialogManager
from aiogram_dialog.api.entities.modes import StartMode
from dishka.integrations.aiogram import FromDishka

from ....bot.dialogs.user_reg.states import CreateProfileSG
from ....services.user_services import UserProfileService, UserRolesService, UserService
from ....utils import has_any_role
from ...filters import create_chat_type_routers
from ...texts import (
    HELP_GROUP,
    HELP_PRIVATE,
    HELP_PRIVATE_PUBLIC,
    INFO_GLOBAL,
    START_GROUP_GREETING,
    START_USER_ERROR,
    render_profile_message,
)

start_private_router, start_group_router, start_global_router = create_chat_type_routers("start")


@start_private_router.message(CommandStart())
@flags.public(True)
async def cmd_start_private(
    message: Message,
    dialog_manager: DialogManager,
    user_service: FromDishka[UserService],
    user_profile_service: FromDishka[UserProfileService],
) -> None:
    if not message.from_user:
        await message.answer(START_USER_ERROR)
        return

    user = await user_service.find_user_by_telegram_id(message.from_user.id)
    if user:
        user_profile_dto = await user_profile_service.build_profile_view(user)
        await message.answer(render_profile_message(user_profile_dto), parse_mode="HTML")
        return

    await dialog_manager.start(CreateProfileSG.welcome, mode=StartMode.RESET_STACK)


@start_global_router.message(CommandStart())
async def cmd_start_group(message: Message) -> None:
    await message.answer(START_GROUP_GREETING)


@start_global_router.message(Command("info"))
async def cmd_info(message: Message) -> None:
    await message.answer(INFO_GLOBAL)


@start_private_router.message(Command("help"))
async def cmd_help_private(message: Message, user_roles_service: FromDishka[UserRolesService], user_id: int) -> None:
    user_roles = await user_roles_service.find_user_roles(user_id)
    if user_roles and has_any_role(set(user_roles), {"Admin"}):
        await message.answer(HELP_PRIVATE)
        return
    await message.answer(HELP_PRIVATE_PUBLIC)


@start_group_router.message(Command("help"))
async def cmd_help_group(message: Message) -> None:
    await message.answer(HELP_GROUP)
