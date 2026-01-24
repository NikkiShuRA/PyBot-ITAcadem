import textwrap

from aiogram.filters import Command
from aiogram.types import Message
from aiogram_dialog import DialogManager
from sqlalchemy.ext.asyncio import AsyncSession

from ....dto import UserReadDTO
from ....services.users import get_user_by_telegram_id
from ...dialogs.user.states import CreateProfileSG
from ...filters import create_chat_type_routers
from ...keyboards.auth import request_contact_kb

grand_profile_private_router, grand_profile_group_router, grand_profile_global_router = create_chat_type_routers("grand_profile")


# /profile - в личном чате
@grand_profile_private_router.message(Command("profile"))
async def cmd_profile_private(message: Message, dialog_manager: DialogManager, db: AsyncSession) -> None:
    if message.from_user:
        user = await get_user_by_telegram_id(db, message.from_user.id)
    else:
        await message.answer(
            "Произошла ошибка при обработке пользователя.",
        )
        return
    if user:
        await show_profile(message, user)
        return
    else:
        await message.answer(
            "Для авторизации отправь свой номер телефона кнопкой ниже.",
            reply_markup=request_contact_kb,
        )
        await dialog_manager.start(CreateProfileSG.contact)
        

# Показ профиля
async def show_profile(message: Message, user: UserReadDTO) -> None:
    await message.answer(
            textwrap.dedent(
                f"""
                👋 Доброго времени суток, {user.first_name}

                📚 Академ уровень — {user.academic_points.value}
                Баллы — {user.academic_points.value} / {{азаза}}

                🤌 Реп уровень — {user.reputation_points.value}
                Баллы — {user.reputation_points.value} / {{азаза}}
                """
            )
        )