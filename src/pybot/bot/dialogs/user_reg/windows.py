from aiogram.types import ContentType
from aiogram_dialog import Dialog, Window
from aiogram_dialog.widgets.input import MessageInput
from aiogram_dialog.widgets.kbd import Back, Cancel, Next
from aiogram_dialog.widgets.text import Const, Format

from .handlers import (
    on_contact_input,
    on_first_name_input,
    on_last_name_input,
    on_other_messages,
    on_patronymic_input,
    on_patronymic_skip,
)
from .states import CreateProfileSG

profile_create_dialog = Dialog(
    Window(
        Const("👤 Твой контакт?"),
        MessageInput(
            on_contact_input,  # ty:ignore[invalid-argument-type]
            content_types=ContentType.CONTACT,
            id="send_contact_info",
        ),
        MessageInput(on_other_messages),
        Cancel(Const("❌ Отмена")),
        state=CreateProfileSG.contact,
    ),
    Window(
        Const("👤 Твоё имя?"),
        MessageInput(on_first_name_input, content_types=ContentType.TEXT),
        Cancel(Const("❌ Отмена")),
        state=CreateProfileSG.first_name,
    ),
    Window(
        Const("👨‍👩 Фамилия?"),
        MessageInput(on_last_name_input, content_types=ContentType.TEXT),
        Back(Const("⬅️ Назад")),
        state=CreateProfileSG.last_name,
    ),
    Window(
        Const("🆔 Отчество?"),
        MessageInput(on_patronymic_input, content_types=ContentType.TEXT),  # ty:ignore[invalid-argument-type]
        Back(Const("⬅️ Назад")),
        Next(Const("➡️ Пропустить"), on_click=on_patronymic_skip),  # ty:ignore[invalid-argument-type]
        state=CreateProfileSG.patronymic,
    ),
    Window(
        Format("✅ Профиль создан. Добро пожаловать, {dialog_data[first_name]}!"),
        state=CreateProfileSG.finish,
    ),
)
