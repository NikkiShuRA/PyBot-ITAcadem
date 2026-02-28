from aiogram.types import CallbackQuery, Contact, Message, ReplyKeyboardRemove
from aiogram_dialog import DialogManager
from aiogram_dialog.widgets.input import MessageInput
from aiogram_dialog.widgets.kbd import Button
from dishka.integrations.aiogram import FromDishka
from dishka.integrations.aiogram_dialog import inject

from ....core import logger
from ....dto import UserCreateDTO
from ....mappers.user_mappers import map_dialog_data_to_user_create_dto
from ....services.users import UserService


def _validate_name_input(raw_text: str, field_name: str, *, allow_empty: bool = False) -> str | None:
    """Validate a name-like input without silently dropping invalid symbols."""
    text = raw_text.strip()
    if not text:
        if allow_empty:
            return None
        raise ValueError(f"Поле «{field_name}» не может быть пустым. Попробуйте снова.")

    cleaned_text = UserCreateDTO.clean_string(text)
    if cleaned_text != text:
        raise ValueError(f"Поле «{field_name}» должно содержать только русские буквы и пробелы.")

    if len(text) < UserCreateDTO.NAME_MIN_LENGTH:
        raise ValueError(f"Поле «{field_name}» слишком короткое.")

    if len(text) > UserCreateDTO.NAME_MAX_LENGTH:
        raise ValueError(f"Поле «{field_name}» слишком длинное. Максимум {UserCreateDTO.NAME_MAX_LENGTH} символов.")

    return text


async def on_other_messages(message: Message, message_input: MessageInput, manager: DialogManager) -> None:
    await message.answer("Пожалуйста, введите корректное значение.")


@inject
async def on_contact_input(
    message: Message,
    message_input: MessageInput,
    manager: DialogManager,
    user_service: FromDishka[UserService],
) -> None:
    await _handle_contact_input(message, manager, user_service)


async def _handle_contact_input(
    message: Message,
    manager: DialogManager,
    user_service: UserService,
) -> None:
    contact: Contact | None = message.contact if message.contact else None
    if contact is None or contact.phone_number is None:
        await message.answer("Контакт не может быть пустым. Попробуйте снова.")
        return

    phone: str = contact.phone_number
    user = await user_service.get_user_by_phone(phone)
    if user:
        await message.answer(
            f"Найден существующий профиль. Твой ID: {user.id}",
            reply_markup=ReplyKeyboardRemove(),
        )
        await manager.done()
        return

    manager.dialog_data["phone_number"] = contact.phone_number
    if message.from_user and hasattr(message.from_user, "id"):
        manager.dialog_data["tg_id"] = message.from_user.id
    else:
        manager.dialog_data["tg_id"] = None
    await message.answer("Контакт получен. Продолжаем регистрацию.", reply_markup=ReplyKeyboardRemove())
    await manager.next()


async def on_first_name_input(
    message: Message,
    widget: MessageInput,
    manager: DialogManager,
) -> None:
    first_name = message.text or ""
    try:
        validated_first_name = _validate_name_input(first_name, "Имя")
    except ValueError as err:
        await message.answer(str(err))
        return

    manager.dialog_data["first_name"] = validated_first_name
    await manager.next()


async def on_last_name_input(
    message: Message,
    widget: MessageInput,
    manager: DialogManager,
) -> None:
    last_name = message.text or ""
    try:
        validated_last_name = _validate_name_input(last_name, "Фамилия")
    except ValueError as err:
        await message.answer(str(err))
        return

    manager.dialog_data["last_name"] = validated_last_name
    await manager.next()


@inject
async def on_patronymic_input(
    message: Message,
    widget: MessageInput,
    manager: DialogManager,
    user_service: FromDishka[UserService],
) -> None:
    await _on_patronymic_input_impl(
        message=message,
        widget=widget,
        manager=manager,
        user_service=user_service,
    )


async def _on_patronymic_input_impl(
    message: Message,
    widget: MessageInput,
    manager: DialogManager,
    user_service: UserService,
) -> None:
    patronymic = message.text or ""
    try:
        cleaned_patronymic = _validate_name_input(patronymic, "Отчество", allow_empty=True)
    except ValueError as err:
        await message.answer(str(err))
        return

    manager.dialog_data["patronymic"] = cleaned_patronymic
    user_data = await map_dialog_data_to_user_create_dto(manager)
    if not user_data:
        await message.answer("Внутренняя ошибка. Пожалуйста, начните заново: /start")
        await manager.done()
        return

    user = await user_service.register_student(user_data)
    if not user:
        await message.answer("Внутренняя ошибка. Пожалуйста, начните заново: /start")
        await manager.done()
        return

    logger.info("User created: {user}", user=user)
    await message.answer(f"✅ Профиль создан. Добро пожаловать, {user.first_name}!")
    await manager.done()


@inject
async def on_patronymic_skip(
    callback: CallbackQuery,
    button: Button,
    manager: DialogManager,
    user_service: FromDishka[UserService],
) -> None:
    user_data = await map_dialog_data_to_user_create_dto(manager)
    if not user_data:
        await callback.answer("Внутренняя ошибка. Пожалуйста, начните заново: /start")
        await manager.done()
        return

    user = await user_service.register_student(user_data)
    if user is None:
        await callback.answer("Внутренняя ошибка. Пожалуйста, начните заново: /start")
        await manager.done()
        return

    logger.info("User created: {user}", user=user)
    if callback.message is not None:
        await callback.message.answer(f"✅ Профиль создан. Добро пожаловать, {user.first_name}!")
    await callback.answer()
    await manager.done()
