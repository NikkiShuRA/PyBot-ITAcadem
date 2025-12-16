from aiogram.types import CallbackQuery, Message
from aiogram_dialog import DialogManager
from aiogram_dialog.widgets.input import MessageInput
from aiogram_dialog.widgets.kbd import Button
from pydantic import ValidationError
from sqlalchemy.ext.asyncio import AsyncSession

from ....core import logger
from ....dto import UserCreateDTO
from ....services.users import create_user_profile


async def on_first_name_input(
    message: Message,
    widget: MessageInput,
    manager: DialogManager,
) -> None:
    """Обработка ввода имени."""
    first_name: str = message.text.strip() if message.text else ""
    if not first_name:
        await message.answer("❌ Имя не может быть пустым. Попробуйте снова.")
        return

    manager.dialog_data["first_name"] = first_name
    await manager.next()


async def on_last_name_input(
    message: Message,
    widget: MessageInput,
    manager: DialogManager,
) -> None:
    """Обработка ввода фамилии (опционально)."""
    text = message.text.strip() if message.text else ""
    last_name = text if text else None

    manager.dialog_data["last_name"] = last_name
    await manager.next()


async def on_patronymic_input(
    message: Message,
    widget: MessageInput,
    manager: DialogManager,
) -> None:
    """Обработка ввода отчества и создание профиля."""
    text = message.text.strip() if message.text else ""
    patronymic = text if text else None
    phone = manager.dialog_data.get("phone")
    tg_id = manager.dialog_data.get("tg_id")
    first_name = manager.dialog_data.get("first_name")

    if not (phone and tg_id and first_name):
        logger.error(
            f"Недостаточно данных для создания профиля. phone: {phone}, tg_id: {tg_id}, first_name: {first_name}"
        )
        await message.answer("Произошла внутренняя ошибка. Пожалуйста, начните заново /start")
        await manager.done()
        return

    # Собираем данные в DTO
    try:
        user_data = UserCreateDTO(
            phone=phone,
            tg_id=tg_id,
            first_name=first_name,
            last_name=manager.dialog_data.get("last_name"),
            patronymic=patronymic,
        )
    except (ValidationError, TypeError):
        logger.exception("Ошибка валидации данных для создания профиля")
        await message.answer("Произошла ошибка с данными. Пожалуйста, начните заново /start")
        await manager.done()
        return

    db: AsyncSession = manager.middleware_data["db"]

    user = await create_user_profile(db, data=user_data)

    logger.info(f"Создан user: {user}")
    manager.dialog_data["user_id"] = user.id
    await manager.next()


async def on_patronymic_skip(callback: CallbackQuery, button: Button, manager: DialogManager) -> None:
    phone = manager.dialog_data.get("phone")
    tg_id = manager.dialog_data.get("tg_id")
    first_name = manager.dialog_data.get("first_name")

    if not (phone and tg_id and first_name):
        logger.error(
            f"Недостаточно данных для создания профиля. phone: {phone}, tg_id: {tg_id}, first_name: {first_name}"
        )
        await callback.answer("Произошла внутренняя ошибка. Пожалуйста, начните заново /start")
        await manager.done()
        return

    try:
        user_data = UserCreateDTO(
            phone=phone,
            tg_id=tg_id,
            first_name=first_name,
            last_name=manager.dialog_data.get("last_name"),
            patronymic=None,
        )
    except (ValidationError, TypeError):
        logger.exception("Ошибка валидации данных для создания профиля")
        await callback.answer("Произошла ошибка с данными. Пожалуйста, начните заново /start")
        await manager.done()
        return

    db: AsyncSession = manager.middleware_data["db"]

    user = await create_user_profile(db, data=user_data)
    logger.info(f"Создан user: {user}")
    manager.dialog_data["user_id"] = user.id
