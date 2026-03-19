from aiogram.types import ContentType
from aiogram_dialog import Dialog, Window
from aiogram_dialog.widgets.input import MessageInput
from aiogram_dialog.widgets.kbd import Back, Button, Cancel
from aiogram_dialog.widgets.text import Const

from ...texts import (
    BUTTON_CONTINUE,
    REGISTRATION_CONTACT_STEP,
    REGISTRATION_FIRST_NAME_STEP,
    REGISTRATION_LAST_NAME_STEP,
    REGISTRATION_PATRONYMIC_STEP,
    REGISTRATION_WELCOME,
    button_back,
    button_cancel,
    button_skip,
)
from .handlers import (
    on_contact_input,
    on_first_name_input,
    on_last_name_input,
    on_other_messages,
    on_patronymic_input,
    on_patronymic_skip,
    request_contact_prompt,
)
from .states import CreateProfileSG

profile_create_dialog = Dialog(
    Window(
        Const(REGISTRATION_WELCOME),
        Button(
            Const(BUTTON_CONTINUE),
            id="go_to_contact",
            on_click=request_contact_prompt,
        ),
        Cancel(Const(button_cancel())),
        state=CreateProfileSG.welcome,
    ),
    Window(
        Const(REGISTRATION_CONTACT_STEP),
        MessageInput(
            on_contact_input,  # ty:ignore[invalid-argument-type]
            content_types=ContentType.CONTACT,
            id="send_contact_info",
        ),
        MessageInput(on_other_messages),
        Cancel(Const(button_cancel())),
        state=CreateProfileSG.contact,
    ),
    Window(
        Const(REGISTRATION_FIRST_NAME_STEP),
        MessageInput(on_first_name_input, content_types=ContentType.TEXT),
        Cancel(Const(button_cancel())),
        state=CreateProfileSG.first_name,
    ),
    Window(
        Const(REGISTRATION_LAST_NAME_STEP),
        MessageInput(on_last_name_input, content_types=ContentType.TEXT),
        Back(Const(button_back())),
        state=CreateProfileSG.last_name,
    ),
    Window(
        Const(REGISTRATION_PATRONYMIC_STEP),
        MessageInput(on_patronymic_input, content_types=ContentType.TEXT),  # ty:ignore[invalid-argument-type]
        Back(Const(button_back())),
        Button(
            Const(button_skip()),
            id="skip_patronymic",
            on_click=on_patronymic_skip,  # ty:ignore[invalid-argument-type]
        ),
        state=CreateProfileSG.patronymic,
    ),
)
