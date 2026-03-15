from collections.abc import Awaitable, Callable
from typing import Any

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject
from dishka.integrations.aiogram import CONTAINER_NAME
from sqlalchemy.ext.asyncio import AsyncSession

from ...core import logger
from ...infrastructure.user_repository import UserRepository


class UserActivityMiddleware(BaseMiddleware):
    """Middleware to update user's last activity timestamp."""

    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: dict[str, Any],
    ) -> Any:
        # 2. 🕵️‍♂️ Фоновая логика трекинга (выполняется после ответа)
        user = data.get("event_from_user")
        if not user:
            return await handler(event, data)

        container = data.get(CONTAINER_NAME)
        if not container:
            # Логируем ошибку, но не ломаем работу бота, результат возвращаем
            logger.error("❌ Dishka container not found in data!")
            return await handler(event, data)

        try:
            async with container() as request_container:
                db: AsyncSession = await request_container.get(AsyncSession)
                repo: UserRepository = await request_container.get(UserRepository)
                # TODO Лучше заменить на application service
                db_user = await repo.find_user_by_telegram_id(db, tg_id=user.id)
                if db_user:
                    await repo.update_user_last_active(db=db, user_id=db_user.id)
                    data["user_id"] = db_user.id  # Добавляем user_id для отвязки логики в сервисах от telegram id
                    data["user_roles"] = set(await repo.find_user_roles(db=db, user_id=db_user.id))
                    await db.commit()

        except Exception:
            logger.exception("Failed to update user activity")
            raise

        return await handler(event, data)
