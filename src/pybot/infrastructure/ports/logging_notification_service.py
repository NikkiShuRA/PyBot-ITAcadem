from collections import deque

from ...core import logger
from ...core.config import BotSettings
from ...dto import NotificationLogEvent, NotifyDTO
from ...services.ports import NotificationPermanentError, NotificationPort
from ...utils import telegram_user_link


class LoggingNotificationService(NotificationPort):
    """Notification adapter that writes outbound events to loguru logger."""

    def __init__(self, settings: BotSettings, buffer_size: int = 1000) -> None:
        if buffer_size <= 0:
            raise ValueError("buffer_size must be greater than 0")
        self._settings = settings
        self._events: deque[NotificationLogEvent] = deque(maxlen=buffer_size)

    @property
    def events(self) -> tuple[NotificationLogEvent, ...]:
        """Expose immutable snapshot of buffered notification events."""
        return tuple(self._events)

    async def send_role_request_to_admin(self, request_id: int, requester_user_id: int, role_name: str) -> None:
        """Log role request notification with payload and store event in ring buffer."""
        admin_tg_id = self._settings.role_request_admin_tg_id

        mention = telegram_user_link(requester_user_id)
        text = f"New role request\n\nRequest ID: {request_id}\nRole: {role_name}\nUser: {mention}"
        event = NotificationLogEvent(
            event_type="role_request_to_admin",
            recipient_id=admin_tg_id,
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
        except Exception as exc:
            logger.exception(
                "Failed to log role request notification | admin_tg_id={admin_tg_id} request_id={request_id}",
                admin_tg_id=admin_tg_id,
                request_id=request_id,
            )
            raise NotificationPermanentError(message="Failed to log role request notification") from exc

    async def send_message(self, message_data: NotifyDTO) -> None:
        """Log direct message notification and store event in ring buffer."""
        recipient_id, cleaned_text = message_data.recipient_id, message_data.message

        event = NotificationLogEvent(
            event_type="direct_message",
            recipient_id=recipient_id,
            message_text=cleaned_text,
        )

        try:
            logger.info(
                "Direct notification (logging backend) | recipient_id={recipient_id} "
                "message_preview={message_preview} parse_mode={parse_mode}",
                recipient_id=recipient_id,
                message_preview=cleaned_text[:120],
                parse_mode=message_data.parse_mode,
            )
            self._events.append(event)
        except Exception as exc:
            logger.exception(
                "Failed to log direct notification | recipient_id={recipient_id} "
                "message_preview={message_preview} parse_mode={parse_mode}",
                recipient_id=recipient_id,
                message_preview=cleaned_text[:120],
                parse_mode=message_data.parse_mode,
            )
            raise NotificationPermanentError(message="Failed to log direct notification") from exc
