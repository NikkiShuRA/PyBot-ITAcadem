import time
from collections.abc import Awaitable, Callable
from typing import Any

from aiogram import BaseMiddleware
from aiogram.types import CallbackQuery, ChatMemberUpdated, InlineQuery, Message, TelegramObject

from ...core import logger
from ...core.config import settings


class LoggerMiddleware(BaseMiddleware):
    def __init__(self, enabled: bool = True, log_sensitive: bool = False) -> None:
        """
        enabled: включить ли логирование
        log_sensitive: логировать ли sensitive данные
        """
        super().__init__()
        self.enabled = settings.enable_logging_middleware and enabled

    def _extract_minimal_info(self, telegram_obj: TelegramObject, data: dict[str, Any]) -> dict[str, Any]:
        """
        ✅ Извлекаем МИНИМАЛЬНО необходимую информацию из TelegramObject
        (никаких None значений, объектов, мусора)

        Работает с: Message, CallbackQuery, InlineQuery, ChatMemberUpdated
        """
        info = {
            "event_type": "UNKNOWN",
            "user_id": None,
            "username": "unknown",
            "chat_id": None,
            "chat_type": "unknown",
            "content": "",
            "user_role": None,  # TODO: Извлекать из data, если нужно (пока None)
            "can_access": None,  # TODO: Извлекать из data, если нужно (пока None)
        }

        # LBYL: Поддерживаемые типы (fail-fast для unknown)
        supported_types = (Message, CallbackQuery, InlineQuery, ChatMemberUpdated)
        if not isinstance(telegram_obj, supported_types):
            logger.debug("⚠️ Unsupported TelegramObject type: {type}", type=type(telegram_obj).__name__)
            return info

        # Match в порядке приоритета/частоты (Message — самый common)
        match telegram_obj:
            case Message():
                self._extract_message_info(telegram_obj, info)
            case CallbackQuery():
                self._extract_callback_info(telegram_obj, info)
            case InlineQuery():
                self._extract_inline_info(telegram_obj, info)
            case ChatMemberUpdated():
                self._extract_member_updated_info(telegram_obj, info)

        return info

    def _extract_message_info(self, obj: Message, info: dict[str, Any]) -> None:
        """Стратегия для Message: Извлечение user/chat/content"""
        info["event_type"] = "MESSAGE"

        if obj.from_user:
            info["user_id"] = obj.from_user.id
            info["username"] = obj.from_user.username or "noname"
            logger.debug("Extracted user from Message: {user_id}", user_id=info["user_id"])

        if obj.chat:
            info["chat_id"] = obj.chat.id
            info["chat_type"] = obj.chat.type

        if obj.text:
            info["content"] = obj.text
        elif obj.caption:
            info["content"] = f"[{obj.content_type}] {obj.caption}"
        else:
            info["content"] = f"[{obj.content_type}]"

    def _extract_callback_info(self, obj: CallbackQuery, info: dict[str, Any]) -> None:
        """Стратегия для CallbackQuery"""
        info["event_type"] = "CALLBACK"

        if obj.from_user:
            info["user_id"] = obj.from_user.id
            info["username"] = obj.from_user.username or "noname"
            logger.debug("Extracted user from Callback: {user_id}", user_id=info["user_id"])

        if obj.message and obj.message.chat:
            info["chat_id"] = obj.message.chat.id
            info["chat_type"] = obj.message.chat.type

        if obj.data:
            info["content"] = f"[button] {obj.data}"

    def _extract_inline_info(self, obj: InlineQuery, info: dict[str, Any]) -> None:
        """Стратегия для InlineQuery"""
        info["event_type"] = "INLINE"

        if obj.from_user:
            info["user_id"] = obj.from_user.id
            info["username"] = obj.from_user.username or "noname"
            logger.debug("Extracted user from Inline: {user_id}", user_id=info["user_id"])

        if obj.query:
            info["content"] = f"[search] {obj.query}"

    def _extract_member_updated_info(self, obj: ChatMemberUpdated, info: dict[str, Any]) -> None:
        """Стратегия для ChatMemberUpdated"""
        info["event_type"] = "MEMBER_STATUS"

        if obj.from_user:
            info["user_id"] = obj.from_user.id
            info["username"] = obj.from_user.username or "noname"
            logger.debug("Extracted user from MemberUpdated: {user_id}", user_id=info["user_id"])

        if obj.chat:
            info["chat_id"] = obj.chat.id
            info["chat_type"] = obj.chat.type

        old_status = obj.old_chat_member.status if obj.old_chat_member else "unknown"
        new_status = obj.new_chat_member.status if obj.new_chat_member else "unknown"
        info["content"] = f"{old_status} -> {new_status}"

    def _get_handler_name(self, data: dict[str, Any]) -> str:
        """
        ✅ Получаем имя handler'а (НЕ выгружаем весь объект!)
        """
        if "handler" in data:
            handler = data["handler"]
            if hasattr(handler, "callback"):
                callback = handler.callback
                if hasattr(callback, "__name__"):
                    return callback.__name__

        return "unknown_handler"

    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: dict[str, Any],
    ) -> Any:
        if not self.enabled:
            return await handler(event, data)

        event_info = self._extract_minimal_info(event, data)
        logger.log(
            settings.log_level,
            "📬 [{event_type}] User: {user_id} (@{username}) | Chat: {chat_id} ({chat_type}) | Content: {content}",
            event_type=event_info["event_type"],
            user_id=event_info["user_id"],
            username=event_info["username"],
            chat_id=event_info["chat_id"],
            chat_type=event_info["chat_type"],
            content=event_info["content"][:80],  # Первые 80 символов!
        )

        start_time = time.time()

        try:
            result = await handler(event, data)
            elapsed = time.time() - start_time

            # Логируем успешную обработку
            logger.log(
                settings.log_level,
                "✅ [{event_type}] Success | Handler: {handler_name} | Elapsed: {elapsed:.0f}ms",
                event_type=event_info["event_type"],
                handler_name=self._get_handler_name(data),
                elapsed=elapsed * 1000,
            )

            # Если долго обрабатывалось - WARNING
            if elapsed > 1.0:
                logger.warning(
                    "⚠️ SLOW_HANDLER [{event_type}] took {elapsed:.2f}s | Handler: {handler_name}",
                    event_type=event_info["event_type"],
                    elapsed=elapsed,
                    handler_name=self._get_handler_name(data),
                )

        except Exception as e:
            elapsed = time.time() - start_time

            # Логируем ошибку КОМПАКТНО
            logger.error(
                "❌ [{event_type}] ERROR | Handler: {handler_name} | Error: {error} | Elapsed: {elapsed:.0f}ms",
                event_type=event_info["event_type"],
                handler_name=self._get_handler_name(data),
                error=str(e)[:100],  # Первые 100 символов ошибки
                elapsed=elapsed * 1000,
                exc_info=True,  # Stacktrace в ERROR логе
            )

            raise
        else:
            return result
