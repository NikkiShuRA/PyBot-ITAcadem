from collections import deque
from dataclasses import dataclass
from typing import Literal

from ...core import logger
from ...core.config import settings
from ...services.ports import NotificationPort


@dataclass(frozen=True, slots=True)
class NotificationLogEvent:
    event_type: Literal["role_request_to_admin", "direct_message"]
    recipient_user_id: int
    message_text: str
    request_id: int | None = None
    requester_user_id: int | None = None
    role_name: str | None = None


class LoggingNotificationService(NotificationPort):
    """Notification adapter that writes outbound events to loguru logger."""

    def __init__(self, buffer_size: int = 1000) -> None:
        if buffer_size <= 0:
            raise ValueError("buffer_size must be greater than 0")
        self._events: deque[NotificationLogEvent] = deque(maxlen=buffer_size)

    @property
    def events(self) -> tuple[NotificationLogEvent, ...]:
        """Expose immutable snapshot of buffered notification events."""
        return tuple(self._events)

    async def send_role_request_to_admin(self, request_id: int, requester_user_id: int, role_name: str) -> None:
        """Log role request notification with payload and store event in ring buffer."""
        admin_tg_id = settings.role_request_admin_tg_id
        if admin_tg_id <= 0:
            logger.error(
                "Invalid ROLE_REQUEST_ADMIN_TG_ID configuration: {admin_tg_id}",
                admin_tg_id=admin_tg_id,
            )
            raise ValueError("ROLE_REQUEST_ADMIN_TG_ID must be configured and greater than 0")

        mention = f"<a href='tg://user?id={requester_user_id}'>user {requester_user_id}</a>"
        text = f"New role request\n\nRequest ID: {request_id}\nRole: {role_name}\nUser: {mention}"
        event = NotificationLogEvent(
            event_type="role_request_to_admin",
            recipient_user_id=admin_tg_id,
            message_text=text,
            request_id=request_id,
            requester_user_id=requester_user_id,
            role_name=role_name,
        )

        try:
            logger.info(
                "Role request notification (logging backend) | "
                "admin_tg_id={admin_tg_id} request_id={request_id} "
                "requester_user_id={requester_user_id} role_name={role_name}",
                admin_tg_id=admin_tg_id,
                request_id=request_id,
                requester_user_id=requester_user_id,
                role_name=role_name,
            )
            self._events.append(event)
        except Exception:
            logger.exception(
                "Failed to log role request notification | admin_tg_id={admin_tg_id} request_id={request_id}",
                admin_tg_id=admin_tg_id,
                request_id=request_id,
            )
            raise

    async def send_message(self, user_id: int, message_text: str) -> None:
        """Log direct message notification and store event in ring buffer."""
        if user_id <= 0:
            raise ValueError("user_id must be greater than 0")

        cleaned_text = message_text.strip()
        if not cleaned_text:
            raise ValueError("message_text must not be empty")

        event = NotificationLogEvent(
            event_type="direct_message",
            recipient_user_id=user_id,
            message_text=cleaned_text,
        )

        try:
            logger.info(
                "Direct notification (logging backend) | user_id={user_id} message_preview={message_preview}",
                user_id=user_id,
                message_preview=cleaned_text[:120],
            )
            self._events.append(event)
        except Exception:
            logger.exception(
                "Failed to log direct notification | user_id={user_id} message_preview={message_preview}",
                user_id=user_id,
                message_preview=cleaned_text[:120],
            )
            raise
