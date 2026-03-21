from collections.abc import Awaitable, Callable
from typing import Any

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject
from dishka.integrations.aiogram import CONTAINER_NAME

from ...core import logger
from ...services import UserRolesService, UserService


class UserActivityMiddleware(BaseMiddleware):
    """Middleware to update user's last activity timestamp."""

    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: dict[str, Any],
    ) -> Any:
        # Background activity tracking for the current Telegram user.
        user = data.get("event_from_user")
        if not user:
            return await handler(event, data)

        container = data.get(CONTAINER_NAME)
        if not container:
            # Log the error but do not break update processing.
            logger.error("Dishka container not found in data!")
            return await handler(event, data)

        try:
            async with container() as request_container:
                user_service: UserService = await request_container.get(UserService)
                user_roles_service: UserRolesService = await request_container.get(UserRolesService)
                user_id = await user_service.track_activity(user.id)
                if user_id is not None:
                    data["user_id"] = user_id  # Decouple downstream logic from Telegram ids.
                    data["user_roles"] = set(await user_roles_service.find_user_roles(user_id))

        except Exception:
            logger.exception("Failed to update user activity")
            raise

        return await handler(event, data)
