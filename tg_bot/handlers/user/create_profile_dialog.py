from typing import Optional

from aiogram.types import Message
from aiogram_dialog import Dialog, Window, DialogManager
from aiogram_dialog.widgets.text import Const, Format
from aiogram_dialog.widgets.input import MessageInput
from aiogram_dialog.widgets.kbd import Cancel, Back
from sqlalchemy.ext.asyncio import AsyncSession

from services.users import create_user_profile
from .states import CreateProfileSG

async def on_profile_start(
    start_data: dict,
    manager: DialogManager,
) -> None:
    # сюда прилетит data из dialog_manager.start(...)
    phone = start_data.get("phone")
    tg_id = start_data.get("tg_id")

    manager.dialog_data["phone"] = phone
    manager.dialog_data["tg_id"] = tg_id


async def on_first_name_input(
    message: Message,
    widget: MessageInput,
    manager: DialogManager,
) -> None:
    """Обработка ввода имени."""
    first_name = message.text.strip() if message.text else ""
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
    last_name = None if text == "-" or not text else text

    manager.dialog_data["last_name"] = last_name
    await manager.next()


async def on_patronymic_input(
    message: Message,
    widget: MessageInput,
    manager: DialogManager,
) -> None:
    """Обработка ввода отчества и создание профиля."""
    text = message.text.strip() if message.text else ""
    patronymic = None if text == "-" or not text else text

    dialog_data = manager.dialog_data
    phone: str = dialog_data.get("phone")
    tg_id: int = dialog_data.get("tg_id")
    if not phone or not tg_id:
        await message.answer("Ошибка: нет данных для создания профиля, попробуй ещё раз /start")
        await manager.done()
        return
    first_name: str = dialog_data.get("first_name")
    last_name: Optional[str] = dialog_data.get("last_name")

    db: AsyncSession = manager.middleware_data["db"]

    user = await create_user_profile(
        db,
        phone=phone,
        tg_id=tg_id,
        first_name=first_name,
        last_name=last_name,
        patronymic=patronymic,
    )

    manager.dialog_data["user_id"] = user.id
    await manager.next()


profile_create_dialog = Dialog(
    Window(
        Const("👤 Как тебя зовут? (имя)"),
        MessageInput(on_first_name_input, filter=lambda m: m.text),
        Cancel(Const("❌ Отмена")),
        state=CreateProfileSG.first_name,
    ),
    Window(
        Const("👨‍👩 Фамилия? (можно пропустить, отправив -)"),
        MessageInput(on_last_name_input, filter=lambda m: m.text),
        Back(Const("⬅️ Назад")),
        state=CreateProfileSG.last_name,
    ),
    Window(
        Const("🆔 Отчество? (можно пропустить, отправив -)"),
        MessageInput(on_patronymic_input, filter=lambda m: m.text),
        Back(Const("⬅️ Назад")),
        state=CreateProfileSG.patronymic,
    ),
    Window(
        Format("✅ Профиль создан. Твой ID: {dialog_data[user_id]}"),
        Cancel(Const("🏠 На главную")),
        state=CreateProfileSG.finish,
    ),
    on_start=on_profile_start,
)
