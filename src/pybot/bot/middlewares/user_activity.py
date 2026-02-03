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
        # 1. 🚀 Сначала выполняем бизнес-логику бота (хендлеры)
        # Пользователь мгновенно получает ответ, не ожидая БД.
        result = await handler(event, data)

        # 2. 🕵️‍♂️ Фоновая логика трекинга (выполняется после ответа)
        user = data.get("event_from_user")
        if not user:
            return result

        container = data.get(CONTAINER_NAME)
        if not container:
            # Логируем ошибку, но не ломаем работу бота, результат возвращаем
            logger.error("❌ Dishka container not found in data!")
            return result

        try:
            async with container() as request_container:
                db = await request_container.get(AsyncSession)
                repo: UserRepository = await request_container.get(UserRepository)

                # Выполняем "слепой" апдейт
                await repo.update_user_last_active(db=db, user_id=user.id)
                data["user_id"] = user.id  # Добавляем user_id для отвязки логики в сервисах от telegram id
                # Коммитим. Если изменения были - они сохранятся.
                # Если 5 минут не прошло - SQL вернет 0 rows, коммит будет пустым (быстро).
                await db.commit()

        except Exception:
            logger.exception("Failed to update user activity")
            raise

        return result
