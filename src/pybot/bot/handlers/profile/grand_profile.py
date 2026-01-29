import textwrap

from aiogram.filters import Command
from aiogram.types import Message
from aiogram_dialog import DialogManager
from sqlalchemy.ext.asyncio import AsyncSession

from ....core.constants import PointsTypeEnum
from ....dto import UserReadDTO
from ....services.levels import get_next_level, get_user_current_level
from ....services.users import get_user_by_telegram_id
from ...dialogs.user_reg.states import CreateProfileSG
from ...filters import create_chat_type_routers
from ...keyboards.auth import request_contact_kb
from ...utils import progress_bar

# !!! Сомнительный нейминг файла и функции, ты начисляешь пользователю профиль?
grand_profile_private_router, grand_profile_group_router, grand_profile_global_router = create_chat_type_routers(
    "grand_profile"
)


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
        await show_profile(message, db, user)
        return
    else:
        await message.answer(
            "Для авторизации отправь свой номер телефона кнопкой ниже.",
            reply_markup=request_contact_kb,
        )
        await dialog_manager.start(CreateProfileSG.contact)


# Показ профиля
async def show_profile(message: Message, db: AsyncSession, user: UserReadDTO) -> None:
    # !!! Выделить весь этот блок запросов в отдельную функцию на уровне бизнес-логики для получения данных для профиля
    academ_res = await get_user_current_level(db, user.id, PointsTypeEnum.ACADEMIC)
    if academ_res is None:
        await message.answer("Ошибочка вышла с поиском academ данных.")  # !!! Более официальное сообщение
        return

    user_academ_level, academ_level_entity = academ_res

    next_academ_level = await get_next_level(db, academ_level_entity, PointsTypeEnum.ACADEMIC)
    if next_academ_level is None:
        await message.answer("Ошибочка: не найден следующий academ уровень (возможно, это максимальный уровень).")
        return

    rep_res = await get_user_current_level(db, user.id, PointsTypeEnum.REPUTATION)
    if rep_res is None:
        await message.answer("Ошибочка вышла с поиском rep данных.")
        return

    user_rep_level, rep_level_entity = rep_res

    next_rep_level = await get_next_level(db, rep_level_entity, PointsTypeEnum.REPUTATION)
    # !!! Учитывая работу логики, такой вариант не является ошибочным
    if next_rep_level is None:
        await message.answer("Ошибочка: не найден следующий rep уровень (возможно, это максимальный уровень).")
        return

    academ_req = next_academ_level.required_points
    rep_req = next_rep_level.required_points

    # !!! Объединить в одно условие с тернарым оператором в message.answer
    if academ_req <= 0:
        await message.answer("Ошибочка: некорректный required_points для academ уровня.")
        return
    if rep_req <= 0:
        await message.answer("Ошибочка: некорректный required_points для rep уровня.")
        return

    # !!! Вывод профиля также вывести в отдельную функцию на уровне приложения,
    # !!! для источнее логики хэндлера, превратив её в функцию высшего порядка, используя композицию функций
    academ_bar = progress_bar(user.academic_points.value, academ_req)
    rep_bar = progress_bar(user.reputation_points.value, rep_req)

    await message.answer(
        textwrap.dedent(
            f"""
                👋 Доброго времени суток, {user.first_name}!

                📚 Академический уровень
                {user_academ_level.level.name}
                {academ_bar}
                {user.academic_points.value} / {academ_req}

                🤌 Репутационный уровень
                {user_rep_level.level.name}
                {rep_bar}
                {user.reputation_points.value} / {rep_req}

                👇 Обновить профиль — /profile
                """
        ),
    )
