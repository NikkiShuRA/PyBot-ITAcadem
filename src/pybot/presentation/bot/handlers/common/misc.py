"""Модуль бота IT Academ."""

from aiogram.filters import Command
from aiogram.types import Message
from dishka import FromDishka

from .....domain.exceptions import UserNotFoundError
from .....services.user_services import UserRolesService, UserService
from ....texts import PING_ANONYMOUS, ping_status
from ...filters import create_chat_type_routers

_, _, misc_global_router = create_chat_type_routers("start")


@misc_global_router.message(Command("ping"), flags={"rate_limit": "expensive", "role": {"Student", "Mentor", "Admin"}})
async def cmd_ping(
    message: Message,
    user_service: FromDishka[UserService],
    user_roles_service: FromDishka[UserRolesService],
    user_id: int,
) -> None:
    """Обработчик команды /ping."""
    if message.from_user is None:
        await message.answer(PING_ANONYMOUS)
        return

    try:
        user = await user_service.get_user(user_id)
    except UserNotFoundError:
        await message.answer(PING_ANONYMOUS)
        return

    is_admin = await user_roles_service.check_user_role(user.id, "Admin")
    await message.answer(ping_status(user.first_name, is_admin))


@misc_global_router.message(Command("chat_id"), flags={"rate_limit": "cheap", "role": {"Admin"}})
async def cmd_chat_id(message: Message) -> None:
    """Возвращает идентификатор текущего чата для отладки и настройки."""
    await message.answer(f"chat.id: {message.chat.id}")
