import operator

from aiogram.types import ContentType
from aiogram_dialog import Dialog, Window
from aiogram_dialog.widgets.input import MessageInput
from aiogram_dialog.widgets.kbd import Back, Button, Cancel, Column, Multiselect, Row
from aiogram_dialog.widgets.text import Const, Format

from ...texts import (
    BUTTON_CONTINUE,
    BUTTON_FINISH_REGISTRATION,
    REGISTRATION_COMPETENCE_STEP,
    REGISTRATION_CONTACT_STEP,
    REGISTRATION_FIRST_NAME_STEP,
    REGISTRATION_LAST_NAME_STEP,
    REGISTRATION_PATRONYMIC_STEP,
    REGISTRATION_WELCOME,
    button_back,
    button_cancel,
    button_skip,
)
from .getters import get_registration_competencies
from .handlers import (
    on_competence_selection_changed,
    on_competence_skip,
    on_competence_submit,
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
    Window(
        Const(REGISTRATION_COMPETENCE_STEP),
        Column(
            Multiselect(
                checked_text=Format("✅ {item[1]}"),
                unchecked_text=Format("{item[1]}"),
                id="registration_competence_select",
                items="registration_competencies",
                item_id_getter=operator.itemgetter(0),
                type_factory=int,
                on_state_changed=on_competence_selection_changed,  # ty:ignore[invalid-argument-type]
            ),
        ),
        Row(
            Back(Const(button_back())),
            Button(
                Const(BUTTON_FINISH_REGISTRATION),
                id="submit_registration",
                on_click=on_competence_submit,  # ty:ignore[invalid-argument-type]
            ),
        ),
        Button(
            Const(button_skip()),
            id="skip_competencies",
            on_click=on_competence_skip,  # ty:ignore[invalid-argument-type]
        ),
        getter=get_registration_competencies,
        state=CreateProfileSG.competencies,
    ),
)
