from collections.abc import Awaitable, Callable
from typing import Any

from aiogram import BaseMiddleware
from aiogram.dispatcher.flags import get_flag
from aiogram.types import Message, TelegramObject
from dishka.integrations.aiogram import CONTAINER_NAME
from sqlalchemy.ext.asyncio import AsyncSession

from ...core import logger
from ...infrastructure.user_repository import UserRepository


class RoleMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: dict[str, Any],
    ) -> Any:
        user = data.get("event_from_user")
        if not user:
            return await handler(event, data)

        container = data.get(CONTAINER_NAME)

        if not container:
            logger.error("❌ Dishka container not found in data!")
            return await handler(event, data)

        async with container() as request_container:
            db = await request_container.get(AsyncSession)
            repo: UserRepository = await request_container.get(UserRepository)

            required_role = get_flag(data, "role")

            if not required_role:
                return await handler(event, data)

            has_permission = await repo.has_role(
                db=db,
                telegram_id=user.id,
                role_name=required_role,  # У тебя в репо аргумент role_name
            )

        logger.info(f"🔒 Checking role '{required_role}' for user {user.id}")

        if has_permission:
            return await handler(event, data)

        logger.warning(f"⛔️ Access denied for user {user.id}. Required: {required_role}")

        if isinstance(event, Message):
            await event.answer("⛔️ У вас недостаточно прав для этой операции.")

        return
