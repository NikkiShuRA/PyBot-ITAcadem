from aiogram.types import CallbackQuery, Contact, Message
from aiogram_dialog import DialogManager
from aiogram_dialog.widgets.input import MessageInput
from aiogram_dialog.widgets.kbd import Button
from dishka.integrations.aiogram import FromDishka
from dishka.integrations.aiogram_dialog import inject
from sqlalchemy.ext.asyncio import AsyncSession

from ....core import logger
from ....dto import UserCreateDTO
from ....mappers.user_mappers import map_dialog_data_to_user_create_dto
from ....services.users import UserService, create_user_profile


async def on_other_messages(message: Message, message_input: MessageInput, manager: DialogManager) -> None:
    """
    Fallback handler for unexpected messages.

    Prompts the user to provide a correct value.

    Args:
        message (Message): The incoming message from the user.
        message_input (MessageInput): The message input widget instance.
        manager (DialogManager): The dialog manager.

    """
    await message.answer("Пожалуйста, введите корректное значение.")


@inject
async def on_contact_input(
    message: Message, message_input: MessageInput, manager: DialogManager, user_service: FromDishka[UserService]
) -> None:
    """
    Handle a received contact message.

    Extracts the phone number from the Contact payload, stores it in dialog_data,
    and advances the dialog to the next step.

    Args:
        message (Message): The incoming message containing Contact.
        message_input (MessageInput): The message input widget instance.
        manager (DialogManager): The dialog manager.

    """
    contact: Contact | None = message.contact if message.contact else None
    if contact is None or contact.phone_number is None:
        await message.answer("❌ Контакт не может быть пустым. Попробуйте снова.")
        return
    phone: str = contact.phone_number
    user = await user_service.get_user_by_phone(phone)
    if user:
        await message.answer(f"Найден существующий профиль. Твой ID: {user.id}")
        return
    manager.dialog_data["phone_number"] = contact.phone_number
    if message.from_user and hasattr(message.from_user, "id"):
        manager.dialog_data["tg_id"] = message.from_user.id
    else:
        manager.dialog_data["tg_id"] = None
    await manager.next()


async def on_first_name_input(
    message: Message,
    widget: MessageInput,
    manager: DialogManager,
) -> None:
    """
    Обработка ввода имени.

    Args:
        message (Message): Сообщение пользователя.
        widget (MessageInput): Вкладка ввода.
        manager (DialogManager): Менеджер диалогов.

    Returns:
        None
    """
    first_name: str | None = message.text if message.text else None

    if not first_name:
        await message.answer("❌ Имя не может быть пустым. Попробуйте снова.")
        return

    cleaned_first_name = UserCreateDTO.clean_string(first_name)

    if not cleaned_first_name or len(cleaned_first_name) < UserCreateDTO.NAME_MIN_LENGTH:
        await message.answer("❌ Имя должно содержать только русские буквы и пробелы, и быть не менее 1 символа.")
        return

    # Здесь можно добавить проверку на max_length, если это критично до сохранения в dialog_data
    if len(cleaned_first_name) > UserCreateDTO.NAME_MAX_LENGTH:
        await message.answer(f"❌ Имя слишком длинное. Максимум {UserCreateDTO.NAME_MAX_LENGTH} символов.")
        return

    manager.dialog_data["first_name"] = cleaned_first_name
    await manager.next()


async def on_last_name_input(
    message: Message,
    widget: MessageInput,
    manager: DialogManager,
) -> None:
    """
    Обработка ввода фамилии (опционально).

    Args:
        message (Message): Сообщение пользователя.
        widget (MessageInput): Вкладка ввода.
        manager (DialogManager): Менеджер диалогов.

    Returns:
        None
    """
    last_name: str | None = message.text if message.text else None

    if not last_name:
        await message.answer("❌ Имя не может быть пустым. Попробуйте снова.")
        return

    cleaned_last_name = UserCreateDTO.clean_string(last_name)

    if not cleaned_last_name or len(cleaned_last_name) < UserCreateDTO.NAME_MIN_LENGTH:
        await message.answer("❌ Фамилия должна содержать только русские буквы и пробелы, и быть не менее 1 символа.")
        return

    if len(cleaned_last_name) > UserCreateDTO.NAME_MAX_LENGTH:
        await message.answer(f"❌ Фамилия слишком длинная. Максимум {UserCreateDTO.NAME_MAX_LENGTH} символов.")
        return

    manager.dialog_data["last_name"] = cleaned_last_name
    await manager.next()


async def on_patronymic_input(
    message: Message,
    widget: MessageInput,
    manager: DialogManager,
) -> None:
    """
    Обработка ввода отчества и создание профиля.

    Args:
        message (Message): Сообщение пользователя.
        widget (MessageInput): Вкладка ввода.
        manager (DialogManager): Менеджер диалогов.

    Returns:
        None
    """
    patronymic = message.text if message.text else None
    cleaned_patronymic = None
    if patronymic:
        cleaned_patronymic = UserCreateDTO.clean_string(patronymic)
        if cleaned_patronymic and len(cleaned_patronymic) < UserCreateDTO.NAME_MIN_LENGTH:
            await message.answer(
                "❌ Отчество должно содержать только русские буквы и пробелы, и быть не менее 1 символа."
            )
            return

        if cleaned_patronymic and len(cleaned_patronymic) > UserCreateDTO.NAME_MAX_LENGTH:
            await message.answer(f"❌ Отчество слишком длинное. Максимум {UserCreateDTO.NAME_MAX_LENGTH} символов.")
            return
    manager.dialog_data["patronymic"] = cleaned_patronymic
    user_data = await map_dialog_data_to_user_create_dto(manager)

    if not user_data:
        await message.answer("Произошла внутренняя ошибка. Пожалуйста, начните заново /start")
        await manager.done()
        return

    db: AsyncSession = manager.middleware_data["db"]

    user = await create_user_profile(db, data=user_data)

    if not user_data:
        await message.answer("Произошла внутренняя ошибка. Пожалуйста, начните заново.")
        await manager.done()
        return

    logger.info(f"Создан user: {user}")
    manager.dialog_data["user_id"] = user.id
    await manager.next()


async def on_patronymic_skip(callback: CallbackQuery, button: Button, manager: DialogManager) -> None:
    """
    Обработка нажатия кнопки "Пропустить" при вводе отчества.

    Args:
        callback (CallbackQuery): Объект CallbackQuery, представляющий нажатую кнопку.
        button (Button): Объект Button, представляющий кнопку, на которую был нажат.
        manager (DialogManager): Менеджер диалогов.

    Returns:
        None
    """
    user_data = await map_dialog_data_to_user_create_dto(manager)

    if not user_data:
        await callback.answer("Произошла внутренняя ошибка. Пожалуйста, начните заново.")
        await manager.done()
        return

    db: AsyncSession = manager.middleware_data["db"]

    user = await create_user_profile(db, data=user_data)
    logger.info(f"Создан user: {user}")
    manager.dialog_data["user_id"] = user.id
