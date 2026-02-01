from collections.abc import Awaitable, Callable
from typing import Any

from aiocache import SimpleMemoryCache
from aiogram import BaseMiddleware
from aiogram.types import Message, TelegramObject, User
from aiolimiter import AsyncLimiter

from ...core import logger
from ...core.config import settings


class RateLimitMiddleware(BaseMiddleware):
    def __init__(self) -> None:
        super().__init__()
        self.enable_rate_limit = settings.enable_rate_limit
        if self.enable_rate_limit:
            self.limits = {
                "cheap": (settings.rate_limit_cheap, settings.time_limit_cheap),
                "moderate": (settings.rate_limit_moderate, settings.time_limit_moderate),
                "expensive": (settings.rate_limit_expensive, settings.time_limit_expensive),
            }
        self.cache: SimpleMemoryCache = SimpleMemoryCache()

    async def _get_user_limiter(
        self,
        user_id: int,
        command_type: str,
    ) -> AsyncLimiter:
        """Получить или создать лимитер для пользователя и команды"""
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

    def _extract_from_dict(self, handler: Any) -> str | None:
        """Стратегия 1: Из __dict__"""
        flags = handler.__dict__["flags"]
        rate_limit = flags.get("rate_limit")
        if rate_limit:
            logger.info("🚩 Rate limit flag found in __dict__: {rate_limit}", rate_limit=rate_limit)
            return rate_limit
        return None

    def _extract_from_wrapped(self, handler: Any) -> str | None:
        """Стратегия 2: Из __wrapped__"""
        wrapped = handler.__wrapped__
        if hasattr(wrapped, "__dict__") and "flags" in wrapped.__dict__:
            flags = wrapped.__dict__["flags"]
            rate_limit = flags.get("rate_limit")
            if rate_limit:
                logger.info("🚩 Rate limit flag found in __wrapped__: {rate_limit}", rate_limit=rate_limit)
                return rate_limit
        return None

    def _extract_from_callback(self, handler: Any) -> str | None:
        """Стратегия 3: Из callback.flags"""
        callback = handler.callback
        if hasattr(callback, "flags"):
            flags = callback.flags
            rate_limit = flags.get("rate_limit") if isinstance(flags, dict) else None
            if rate_limit:
                logger.info("🚩 Rate limit flag found in callback.flags: {rate_limit}", rate_limit=rate_limit)
                return rate_limit
        return None

    def _extract_rate_limit_type(self, data: dict[str, Any]) -> str | None:
        """
        ✅ Извлечение флага rate_limit из данных обработчика
        """
        try:
            handler = data.get("handler")
            if not handler:
                logger.info("❌ No handler found in data")
                return None

            match handler:
                case obj if hasattr(obj, "__dict__") and "flags" in obj.__dict__:
                    rate_limit = self._extract_from_dict(handler)
                    if rate_limit:
                        return rate_limit
                case obj if hasattr(obj, "__wrapped__"):
                    rate_limit = self._extract_from_wrapped(handler)
                    if rate_limit:
                        return rate_limit
                case obj if hasattr(obj, "callback"):
                    rate_limit = self._extract_from_callback(handler)
                    if rate_limit:
                        return rate_limit

        except Exception as e:
            logger.warning(
                "⚠️ Error extracting rate_limit flags: {error}",
                error=str(e),
            )

        logger.info("❌ No rate_limit flag found in handler")
        return None

    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: dict[str, Any],
    ) -> Any:
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
            command_limit = self._extract_rate_limit_type(data)
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
