from collections.abc import Awaitable, Callable
from typing import Any

from aiogram import BaseMiddleware
from aiogram.dispatcher.flags import get_flag
from aiogram.types import CallbackQuery, Message, TelegramObject
from dishka import FromDishka
from dishka.integrations.aiogram import CONTAINER_NAME
from sqlalchemy.ext.asyncio import AsyncSession

from ...core import logger
from ...infrastructure.user_repository import UserRepository


class RoleMiddleware(BaseMiddleware):
    def __init__(self) -> None:
        super().__init__()
        self.db = FromDishka[AsyncSession]
        self.repo = FromDishka[UserRepository]

    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: dict[str, Any],
    ) -> Any:
        # 1. СТРАТЕГИЯ ИЗВЛЕЧЕНИЯ (Вместо твоих 50 строк)
        # get_flag сам найдет 'role' во flags хендлера
        required_role = get_flag(data, "role")

        # Если роли нет — быстрый выход
        if not required_role:
            return await handler(event, data)

        user = data.get("event_from_user")
        if not user:
            return await handler(event, data)

        logger.info(f"🔒 Checking role '{required_role}' for user {user.id}")

        # 2. ПОЛУЧЕНИЕ ЗАВИСИМОСТЕЙ ЧЕРЕЗ DISHKA
        # Dishka кладет контейнер в data под ключом CONTAINER_NAME
        container = data.get(CONTAINER_NAME)

        if not container:
            logger.error("❌ Dishka container not found in data!")
            return await handler(event, data)

        # 3. SCOPED ЗАПРОС ЗАВИСИМОСТЕЙ
        # Достаем сессию и репо именно для ЭТОГО запроса
        async with container() as request_container:
            db = await request_container.get(AsyncSession)
            repo = await request_container.get(UserRepository)

            # Или, если у тебя UserRepo уже инжектит сессию сам (зависит от твоей настройки),
            # но мы договорились, что repo stateless, значит передаем db руками.

            has_permission = await repo.has_role(
                db=db,
                telegram_id=user.id,
                role_name=required_role,  # У тебя в репо аргумент role_name
            )

        # 4. РЕЗУЛЬТАТ
        if has_permission:
            return await handler(event, data)

        # Отказ в доступе
        logger.warning(f"⛔️ Access denied for user {user.id}. Required: {required_role}")

        if isinstance(event, Message):
            await event.answer("⛔️ У вас недостаточно прав для этой операции.")
        elif isinstance(event, CallbackQuery):
            await event.answer("⛔️ Нет прав.", show_alert=True)

        # Цепочка прерывается, handler не вызывается
        return
