"""Модуль бота IT Academ."""

from __future__ import annotations

import time
from collections.abc import Awaitable, Callable
from typing import Any

from aiogram import BaseMiddleware
from aiogram.dispatcher.flags import get_flag
from aiogram.types import CallbackQuery, ChatMemberUpdated, InlineQuery, Message, TelegramObject

from ....core import logger
from ....core.config import BotSettings
from ....core.constants import LogPolicyKey

MAX_LOGGED_CONTENT_LENGTH = 80


class LoggerMiddleware(BaseMiddleware):
    """Middleware для единообразного логирования жизненного цикла update."""

    def __init__(self, settings: BotSettings, *, enabled: bool = False, log_sensitive: bool = False) -> None:
        """Инициализировать middleware логирования.

        Args:
            enabled: Включить ли middleware явно.
            log_sensitive: Разрешить ли писать полное содержимое сообщений.
            settings: Объект конфигурации бота.
        """
        super().__init__()
        self.log_sensitive = log_sensitive
        self.settings = settings
        self.enabled = self.settings.enable_logging_middleware and enabled

    def _build_event_id(self, telegram_obj: TelegramObject, data: dict[str, Any]) -> str:
        """Собрать корреляционный ключ для логов одного update."""
        event_update = data.get("event_update")
        update_id = getattr(event_update, "update_id", None)
        if isinstance(update_id, int):
            return f"update:{update_id}"

        match telegram_obj:
            case Message(message_id=message_id, chat=chat):
                return f"message:{chat.id}:{message_id}"
            case CallbackQuery(id=callback_id):
                return f"callback:{callback_id}"
            case InlineQuery(id=inline_id):
                return f"inline:{inline_id}"
            case ChatMemberUpdated(chat=chat, from_user=from_user):
                return f"member:{chat.id}:{from_user.id}"
            case _:
                return f"unknown:{id(telegram_obj)}"

    def _extract_minimal_info(
        self,
        telegram_obj: TelegramObject,
        data: dict[str, Any],
        *,
        redact: bool = False,
    ) -> dict[str, Any]:
        """Извлечь минимальную информацию из Telegram update."""
        info = {
            "event_type": "UNKNOWN",
            "event_id": self._build_event_id(telegram_obj, data),
            "user_id": None,
            "username": "unknown",
            "chat_id": None,
            "chat_type": "unknown",
            "content": "",
        }

        supported_types = (Message, CallbackQuery, InlineQuery, ChatMemberUpdated)
        if not isinstance(telegram_obj, supported_types):
            logger.debug(
                "событие=неподдерживаемый_update event_id={event_id} тип={type}",
                event_id=info["event_id"],
                type=type(telegram_obj).__name__,
            )
            return info

        if redact:
            info["content"] = "[REDACTED BY POLICY]"
        else:
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
        """Извлечь полезные поля из Message."""
        info["event_type"] = "MESSAGE"

        if obj.from_user:
            info["user_id"] = obj.from_user.id
            info["username"] = obj.from_user.username or "noname"
            logger.debug(
                "событие=извлечение_пользователя event_id={event_id} источник=message user_id={user_id}",
                event_id=info["event_id"],
                user_id=info["user_id"],
            )

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
        """Извлечь полезные поля из CallbackQuery."""
        info["event_type"] = "CALLBACK"

        if obj.from_user:
            info["user_id"] = obj.from_user.id
            info["username"] = obj.from_user.username or "noname"
            logger.debug(
                "событие=извлечение_пользователя event_id={event_id} источник=callback user_id={user_id}",
                event_id=info["event_id"],
                user_id=info["user_id"],
            )

        if obj.message and obj.message.chat:
            info["chat_id"] = obj.message.chat.id
            info["chat_type"] = obj.message.chat.type

        if obj.data:
            info["content"] = f"[button] {obj.data}"

    def _extract_inline_info(self, obj: InlineQuery, info: dict[str, Any]) -> None:
        """Извлечь полезные поля из InlineQuery."""
        info["event_type"] = "INLINE"

        if obj.from_user:
            info["user_id"] = obj.from_user.id
            info["username"] = obj.from_user.username or "noname"
            logger.debug(
                "событие=извлечение_пользователя event_id={event_id} источник=inline user_id={user_id}",
                event_id=info["event_id"],
                user_id=info["user_id"],
            )

        if obj.query:
            info["content"] = f"[search] {obj.query}"

    def _extract_member_updated_info(self, obj: ChatMemberUpdated, info: dict[str, Any]) -> None:
        """Извлечь полезные поля из ChatMemberUpdated."""
        info["event_type"] = "MEMBER_STATUS"

        if obj.from_user:
            info["user_id"] = obj.from_user.id
            info["username"] = obj.from_user.username or "noname"
            logger.debug(
                "событие=извлечение_пользователя event_id={event_id} источник=member_status user_id={user_id}",
                event_id=info["event_id"],
                user_id=info["user_id"],
            )

        if obj.chat:
            info["chat_id"] = obj.chat.id
            info["chat_type"] = obj.chat.type

        old_status = obj.old_chat_member.status if obj.old_chat_member else "unknown"
        new_status = obj.new_chat_member.status if obj.new_chat_member else "unknown"
        info["content"] = f"{old_status} -> {new_status}"

    def _normalize_content(self, content: str) -> str:
        """Подготовить текст для компактного логирования."""
        if not self.log_sensitive and len(content) > MAX_LOGGED_CONTENT_LENGTH:
            content = content[:MAX_LOGGED_CONTENT_LENGTH]

        return content.replace("\n", "\\n").replace("\r", "\\r") or "-"

    def _get_handler_name(self, data: dict[str, Any]) -> str:
        """Получить имя handler без сериализации всего объекта."""
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
        """Записать старт, завершение и ошибку обработки update."""
        if not self.enabled:
            return await handler(event, data)

        log_policy = get_flag(data, "log_policy")
        redact = False
        if log_policy == LogPolicyKey.STRICT and self.settings.log_policy_strict:
            redact = True

        event_info = self._extract_minimal_info(event, data, redact=redact)
        handler_name = self._get_handler_name(data)

        with logger.contextualize(update_id=event_info["event_id"], request_id=event_info["event_id"]):
            logger.info(
                "событие=получен_update event_id={event_id} тип={event_type} handler={handler_name} "
                'user_id={user_id} username={username} chat_id={chat_id} chat_type={chat_type} content="{content}"',
                event_id=event_info["event_id"],
                event_type=event_info["event_type"],
                handler_name=handler_name,
                user_id=event_info["user_id"],
                username=event_info["username"],
                chat_id=event_info["chat_id"],
                chat_type=event_info["chat_type"],
                content=self._normalize_content(event_info["content"]),
            )

            start_time = time.monotonic()
            try:
                result = await handler(event, data)
                elapsed = time.monotonic() - start_time

                logger.info(
                    "событие=обработан_update event_id={event_id} тип={event_type} handler={handler_name} "
                    "status=success elapsed_ms={elapsed_ms}",
                    event_id=event_info["event_id"],
                    event_type=event_info["event_type"],
                    handler_name=handler_name,
                    elapsed_ms=round(elapsed * 1000),
                )

                if elapsed > 1.0:
                    logger.warning(
                        "событие=медленный_handler event_id={event_id} тип={event_type} handler={handler_name} "
                        "elapsed_ms={elapsed_ms}",
                        event_id=event_info["event_id"],
                        event_type=event_info["event_type"],
                        handler_name=handler_name,
                        elapsed_ms=round(elapsed * 1000),
                    )
            except Exception as exc:
                elapsed = time.monotonic() - start_time
                logger.error(
                    "событие=ошибка_handler event_id={event_id} тип={event_type} handler={handler_name} "
                    'error_type={error_type} error="{error}" elapsed_ms={elapsed_ms}',
                    event_id=event_info["event_id"],
                    event_type=event_info["event_type"],
                    handler_name=handler_name,
                    error_type=type(exc).__name__,
                    error=self._normalize_content(str(exc)[:160]),
                    elapsed_ms=round(elapsed * 1000),
                    exc_info=True,
                )
                raise
            else:
                return result
