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
    first_name: str | None = message.text if message.text else None
    if not first_name:
        await message.answer("Имя не может быть пустым. Попробуйте снова.")
        return

    cleaned_first_name = UserCreateDTO.clean_string(first_name)
    if not cleaned_first_name or len(cleaned_first_name) < UserCreateDTO.NAME_MIN_LENGTH:
        await message.answer("Имя должно содержать только русские буквы и пробелы.")
        return

    if len(cleaned_first_name) > UserCreateDTO.NAME_MAX_LENGTH:
        await message.answer(f"Имя слишком длинное. Максимум {UserCreateDTO.NAME_MAX_LENGTH} символов.")
        return

    manager.dialog_data["first_name"] = cleaned_first_name
    await manager.next()


async def on_last_name_input(
    message: Message,
    widget: MessageInput,
    manager: DialogManager,
) -> None:
    last_name: str | None = message.text if message.text else None
    if not last_name:
        await message.answer("Фамилия не может быть пустой. Попробуйте снова.")
        return

    cleaned_last_name = UserCreateDTO.clean_string(last_name)
    if not cleaned_last_name or len(cleaned_last_name) < UserCreateDTO.NAME_MIN_LENGTH:
        await message.answer("Фамилия должна содержать только русские буквы и пробелы.")
        return

    if len(cleaned_last_name) > UserCreateDTO.NAME_MAX_LENGTH:
        await message.answer(f"Фамилия слишком длинная. Максимум {UserCreateDTO.NAME_MAX_LENGTH} символов.")
        return

    manager.dialog_data["last_name"] = cleaned_last_name
    await manager.next()


@inject
async def on_patronymic_input(
    message: Message,
    widget: MessageInput,
    manager: DialogManager,
    user_service: FromDishka[UserService],
) -> None:
    patronymic = message.text if message.text else None
    cleaned_patronymic = None

    if patronymic:
        cleaned_patronymic = UserCreateDTO.clean_string(patronymic)
        if cleaned_patronymic and len(cleaned_patronymic) < UserCreateDTO.NAME_MIN_LENGTH:
            await message.answer("Отчество должно содержать только русские буквы и пробелы.")
            return

        if cleaned_patronymic and len(cleaned_patronymic) > UserCreateDTO.NAME_MAX_LENGTH:
            await message.answer(f"Отчество слишком длинное. Максимум {UserCreateDTO.NAME_MAX_LENGTH} символов.")
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
