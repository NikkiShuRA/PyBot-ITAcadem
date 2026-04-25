from collections import deque

from ...core import logger
from ...core.config import BotSettings
from ...dto import NotificationLogEvent, NotifyDTO
from ...services.ports import NotificationPermanentError, NotificationPort
from ...utils import telegram_user_link


class LoggingNotificationService(NotificationPort):
    """Адаптер уведомлений, который записывает исходящие события в логгер loguru.

    Используется в основном для отладки или в средах, где отправка реальных сообщений невозможна/нежелательна.
    Хранит ограниченную историю событий в кольцевом буфере.
    """

    def __init__(self, settings: BotSettings, buffer_size: int = 1000) -> None:
        """Инициализирует сервис логирования уведомлений.

        Args:
            settings: Настройки бота.
            buffer_size: Размер кольцевого буфера для хранения истории событий.

        Raises:
            ValueError: Если buffer_size <= 0.
        """
        if buffer_size <= 0:
            raise ValueError("buffer_size must be greater than 0")
        self._settings = settings
        self._events: deque[NotificationLogEvent] = deque(maxlen=buffer_size)

    @property
    def events(self) -> tuple[NotificationLogEvent, ...]:
        """Возвращает неизменяемый снимок буферизованных событий уведомлений.

        Returns:
            tuple[NotificationLogEvent, ...]: Кортеж событий.
        """
        return tuple(self._events)

    async def send_role_request_to_admin(self, request_id: int, requester_user_id: int, role_name: str) -> None:
        """Логирует уведомление о новой заявке на роль для администратора.

        Args:
            request_id: ID заявки.
            requester_user_id: ID пользователя, подавшего заявку.
            role_name: Название запрашиваемой роли.

        Raises:
            NotificationPermanentError: При критической ошибке логирования.
        """
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
        """Логирует прямое сообщение пользователю.

        Args:
            message_data: DTO с данными сообщения.

        Raises:
            NotificationPermanentError: При критической ошибке логирования.
        """
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
