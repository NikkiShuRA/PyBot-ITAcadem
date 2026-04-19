"""Модуль бота IT Academ."""

from collections.abc import Awaitable, Callable
from typing import Any

from aiogram import BaseMiddleware
from aiogram.dispatcher.flags import get_flag
from aiogram.types import Message, TelegramObject
from dishka.integrations.aiogram import CONTAINER_NAME

from pybot.services import UserService

from ...core import logger
from ...utils import has_any_role
from ..texts import ROLE_ACCESS_DENIED, ROLE_AUTH_ERROR


class RoleMiddleware(BaseMiddleware):
    """Класс для RoleMiddleware."""

    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: dict[str, Any],
    ) -> Any:
        """Вспомогательная функция __call__."""
        required_role = get_flag(data, "role")

        if not required_role:
            return await handler(event, data)

        user = data.get("event_from_user")
        if not user:
            return await handler(event, data)

        user_db_id = data.get("user_id")
        if not user_db_id:
            logger.warning("Role check failed: user not found in DB")
            if isinstance(event, Message):
                await event.answer(ROLE_AUTH_ERROR)
            return

        container = data.get(CONTAINER_NAME)
        if not container:
            logger.error("Dishka container not found in data")
            return await handler(event, data)

        async with container() as request_container:
            service: UserService = await request_container.get(UserService)
            permissions = await service.find_all_user_roles(
                user_id=user_db_id,
            )

        logger.info("Checking role '{required_role}' for user {user_id}", required_role=required_role, user_id=user.id)

        if permissions is not None and has_any_role(permissions, required_role):
            return await handler(event, data)

        logger.warning(
            "Access denied for user {user_id}. Required: {required_role}",
            user_id=user.id,
            required_role=required_role,
        )
        if isinstance(event, Message):
            await event.answer(ROLE_ACCESS_DENIED)

        return
