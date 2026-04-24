"""Модуль бота IT Academ."""

from aiogram.filters.command import Command
from aiogram.types import Message
from dishka.integrations.aiogram import FromDishka

from ....core import logger
from ....presentation.texts import ROLE_UNEXPECTED_ERROR, roles_catalog
from ....services.user_services import UserRolesService
from ...filters import create_chat_type_routers

(_, _, role_catalog_global_router) = create_chat_type_routers("role_catalog")


@role_catalog_global_router.message(
    Command("roles"),
    flags={"rate_limit": "moderate"},
)
async def handle_show_all_roles(
    message: Message,
    user_roles_service: FromDishka[UserRolesService],
) -> None:
    """Форматирует текст для ролей."""
    try:
        roles = await user_roles_service.find_all_roles()
    except Exception:
        logger.exception("Unexpected error in handle_show_all_roles")
        await message.reply(ROLE_UNEXPECTED_ERROR)
        return

    await message.reply(
        roles_catalog(roles),
        parse_mode="HTML",
    )
