"""Модуль бота IT Academ."""

from collections.abc import Awaitable, Callable
from typing import Any

from aiocache import SimpleMemoryCache
from aiogram import BaseMiddleware
from aiogram.dispatcher.flags import get_flag
from aiogram.types import Message, TelegramObject, User
from aiolimiter import AsyncLimiter

from ....core import logger
from ....core.config import BotSettings


class RateLimitMiddleware(BaseMiddleware):
    """Класс для RateLimitMiddleware."""

    def __init__(self, settings: BotSettings) -> None:
        """Инициализирует объект."""
        super().__init__()
        self.settings = settings
        self.enable_rate_limit = self.settings.enable_rate_limit
        if self.enable_rate_limit:
            self.limits = {
                "cheap": (self.settings.rate_limit_cheap, self.settings.time_limit_cheap),
                "moderate": (self.settings.rate_limit_moderate, self.settings.time_limit_moderate),
                "expensive": (self.settings.rate_limit_expensive, self.settings.time_limit_expensive),
            }
        self.cache: SimpleMemoryCache = SimpleMemoryCache()

    async def _get_user_limiter(
        self,
        user_id: int,
        command_type: str,
    ) -> AsyncLimiter:
        """Получить или создать лимитер для пользователя и команды."""
        key = f"{user_id}:{command_type}"

        limiter = await self.cache.get(key)

        if limiter is None:
            # Создать новый лимитер
            max_rate, time_period = self.limits.get(
                command_type,
                self.limits["moderate"],
            )
            # Защита от некорректных настроек
            if max_rate <= 0 or time_period <= 0:
                max_rate, time_period = self.limits["moderate"]

            limiter = AsyncLimiter(max_rate=max_rate, time_period=time_period)
            await self.cache.set(key, limiter, ttl=3600)

        return limiter

    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: dict[str, Any],
    ) -> Any:
        """Вспомогательная функция __call__."""
        # 🛑 Rate limit отключён
        if not self.enable_rate_limit:
            return await handler(event, data)

        # 🛑 Только MESSAGE события
        if not isinstance(event, Message):
            return await handler(event, data)

        # 🛑 Нет пользователя
        user: User | None = event.from_user
        if user is None:
            return await handler(event, data)

        try:
            # ✅ ПРАВИЛЬНО: передаём data, а не handler!
            command_limit = get_flag(data, "rate_limit")
            logger.info(f"Extracted rate limit type: {command_limit}")
            if not command_limit:
                logger.info(
                    f"⏭️ No rate limit for user {user.id}",
                )
                return await handler(event, data)

            limiter = await self._get_user_limiter(user.id, command_limit)

            async with limiter:
                logger.info(f"✅ Rate limit APPLIED | User: {user.id} | Type: '{command_limit}'")
                return await handler(event, data)

        except Exception as e:
            logger.error(
                "❌ Rate limit middleware error: {error}",
                error=str(e),
                exc_info=True,
            )

        return await handler(event, data)
