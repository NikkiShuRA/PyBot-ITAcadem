from aiogram.filters import Command
from aiogram.types import Message
from aiogram_dialog import DialogManager
from aiogram_dialog.api.entities.modes import StartMode
from dishka.integrations.aiogram import FromDishka

from ....services import UserProfileService
from ....services.users import UserService
from ...dialogs.user_reg.states import CreateProfileSG
from ...filters import create_chat_type_routers

# !!! Сомнительный нейминг файла и функции, ты начисляешь пользователю профиль?
user_profile_private_router, user_profile_group_router, user_profile_global_router = create_chat_type_routers(
    "user_profile"
)


# /profile - в личном чате
@user_profile_private_router.message(Command("profile"))
async def cmd_profile_private(
    message: Message,
    dialog_manager: DialogManager,
    user_service: FromDishka[UserService],
    user_profile_service: FromDishka[UserProfileService],
) -> None:
    if message.from_user:
        user = await user_service.find_user_by_telegram_id(message.from_user.id)
        if user:
            await user_profile_service.manage_profile(user)
            return

    await dialog_manager.start(CreateProfileSG.contact, mode=StartMode.RESET_STACK)
