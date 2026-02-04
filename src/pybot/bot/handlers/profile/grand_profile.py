import textwrap

from aiogram.filters import Command
from aiogram.types import Message
from aiogram_dialog import DialogManager
from dishka.integrations.aiogram import FromDishka
from sqlalchemy.ext.asyncio import AsyncSession

from ....core.constants import LevelTypeEnum
from ....dto import UserReadDTO
from ....services.users import UserService, collect_user_profile
from ...dialogs.user_reg.states import CreateProfileSG
from ...filters import create_chat_type_routers
from ...utils.text_ui import progress_bar

# !!! Сомнительный нейминг файла и функции, ты начисляешь пользователю профиль?
grand_profile_private_router, grand_profile_group_router, grand_profile_global_router = create_chat_type_routers(
    "grand_profile"
)


# /profile - в личном чате
@grand_profile_private_router.message(Command("profile"))
async def cmd_profile_private(
    message: Message,
    dialog_manager: DialogManager,
    user_service: FromDishka[UserService],
    db: FromDishka[AsyncSession],
) -> None:
    if message.from_user:
        user = await user_service.get_user_by_telegram_id(message.from_user.id)
    else:
        await message.answer(
            "Произошла ошибка при обработке пользователя.",
        )
        return
    if user:
        await show_profile(message, db, user)
        return
    else:
        await message.answer(
            "Пожалуйста, отправьте свой контакт, используя кнопку ниже.",
        )
        await dialog_manager.start(CreateProfileSG.contact)


# !!!   НУЖНО ДОРАБОТАТЬ
# Показ профиля
async def show_profile(message: Message, db: AsyncSession, user_read: UserReadDTO) -> None:
    user_profile = await collect_user_profile(db, user_read)
    academ_bar = await progress_bar(user_profile.user.academic_points.value, user_profile.level_info[0].next_level.required_points)
    rep_bar = await progress_bar(user_profile.user.reputation_points.value, user_profile.level_info[1].next_level.required_points)

    await message.answer(
        textwrap.dedent(
            f"""
                👋 Доброго времени суток, {user_profile.user.first_name}!

                📚 Академический уровень
                {user_profile.level_info[0].curret_level.name}
                {academ_bar}
                {user_profile.user.academic_points.value} / {user_profile.level_info[0].next_level.required_points}

                🤌 Репутационный уровень
                {user_profile.level_info[1].curret_level.name}
                {rep_bar}
                {user_profile.user.reputation_points.value} / {user_profile.level_info[1].next_level.required_points}

                👇 Обновить профиль — /profile
                """
        ),
    )
