from aiogram import Bot
from aiogram.exceptions import (
    RestartingTelegram,
    TelegramAPIError,
    TelegramBadRequest,
    TelegramEntityTooLarge,
    TelegramForbiddenError,
    TelegramNetworkError,
    TelegramNotFound,
    TelegramRetryAfter,
    TelegramServerError,
    TelegramUnauthorizedError,
)

from ...core import logger
from ...core.config import BotSettings
from ...dto import NotifyDTO
from ...presentation.bot import get_admin_decision_kb
from ...presentation.texts import role_request_admin_notification
from ...services.ports import NotificationPermanentError, NotificationPort, NotificationTemporaryError
from ...utils import telegram_user_link


class TelegramNotificationService(NotificationPort):
    """Реализация NotificationPort для отправки уведомлений через Telegram Bot API.

    Обеспечивает доставку уведомлений о заявках на роли администраторам и прямых сообщений пользователям.
    Обрабатывает типичные ошибки Telegram API (Rate Limits, Forbidden, и т.д.), транслируя их в доменные исключения.
    """

    def __init__(self, bot: Bot, settings: BotSettings) -> None:
        """Инициализирует сервис уведомлений Telegram.

        Args:
            bot: Экземпляр бота aiogram.
            settings: Настройки приложения.
        """
        self.bot = bot
        self._settings = settings

    async def send_role_request_to_admin(self, request_id: int, requester_user_id: int, role_name: str) -> None:
        """Отправляет уведомление о новой заявке на роль администратору.

        Args:
            request_id: ID заявки.
            requester_user_id: ID пользователя, подавшего заявку.
            role_name: Название запрашиваемой роли.

        Raises:
            NotificationTemporaryError: При временных сбоях (Rate limit, сетевые ошибки).
            NotificationPermanentError: При критических ошибках API или неожиданных сбоях.
        """
        admin_tg_id = self._settings.role_request_admin_tg_id
        mention = telegram_user_link(requester_user_id)
        text = role_request_admin_notification(request_id=request_id, role_name=role_name, mention=mention)

        try:
            await self.bot.send_message(
                chat_id=admin_tg_id,
                text=text,
                parse_mode="HTML",
                reply_markup=get_admin_decision_kb(request_id),
            )
        except TelegramRetryAfter as exc:
            logger.warning(
                "Telegram retry-after while sending message | user_id={user_id} retry_after={retry_after}",
                user_id=requester_user_id,
                retry_after=exc.retry_after,
            )
            raise NotificationTemporaryError(
                message="Telegram rate limit encountered",
                retry_after_seconds=float(exc.retry_after),
            ) from exc
        except (TelegramNetworkError, TelegramServerError, RestartingTelegram) as exc:
            logger.warning(
                "Temporary Telegram failure while sending message | user_id={user_id} error={error}",
                user_id=requester_user_id,
                error=str(exc),
            )
            raise NotificationTemporaryError(message="Temporary Telegram delivery failure") from exc
        except (
            TelegramBadRequest,
            TelegramForbiddenError,
            TelegramUnauthorizedError,
            TelegramNotFound,
            TelegramEntityTooLarge,
        ) as exc:
            logger.warning(
                "Permanent Telegram failure while sending message | user_id={user_id} error={error}",
                user_id=requester_user_id,
                error=str(exc),
            )
            raise NotificationPermanentError(message="Permanent Telegram delivery failure") from exc
        except TelegramAPIError as exc:
            logger.warning(
                "Telegram API error while sending message | user_id={user_id} error={error}",
                user_id=requester_user_id,
                error=str(exc),
            )
            raise NotificationPermanentError(message="Telegram API delivery failure") from exc
        except Exception as exc:
            logger.exception(
                "Failed to send role request notification | "
                "admin_tg_id={admin_tg_id} request_id={request_id} "
                "requester_user_id={requester_user_id} role_name={role_name}",
                admin_tg_id=admin_tg_id,
                request_id=request_id,
                requester_user_id=requester_user_id,
                role_name=role_name,
            )
            raise NotificationPermanentError(message="Unexpected notification delivery failure") from exc

    async def send_message(self, message_data: NotifyDTO) -> None:
        """Отправляет прямое сообщение пользователю.

        Args:
            message_data: DTO с данными сообщения (текст, получатель, parse_mode).

        Raises:
            NotificationTemporaryError: При временных сбоях.
            NotificationPermanentError: При критических ошибках API.
        """
        cleaned_text = message_data.message
        recipient_id = message_data.recipient_id
        parse_mode = message_data.parse_mode
        message_thread_id = message_data.message_thread_id

        try:
            await self.bot.send_message(
                chat_id=recipient_id,
                message_thread_id=message_thread_id,
                text=cleaned_text,
                parse_mode=parse_mode,
            )
        except TelegramRetryAfter as exc:
            logger.warning(
                "Telegram retry-after while sending message | recipient_id={recipient_id} retry_after={retry_after}",
                recipient_id=recipient_id,
                retry_after=exc.retry_after,
            )
            raise NotificationTemporaryError(
                message="Telegram rate limit encountered",
                retry_after_seconds=float(exc.retry_after),
            ) from exc
        except (TelegramNetworkError, TelegramServerError, RestartingTelegram) as exc:
            logger.warning(
                "Temporary Telegram failure while sending message | recipient_id={recipient_id} error={error}",
                recipient_id=recipient_id,
                error=str(exc),
            )
            raise NotificationTemporaryError(message="Temporary Telegram delivery failure") from exc
        except (
            TelegramBadRequest,
            TelegramForbiddenError,
            TelegramUnauthorizedError,
            TelegramNotFound,
            TelegramEntityTooLarge,
        ) as exc:
            logger.warning(
                "Permanent Telegram failure while sending message | recipient_id={recipient_id} error={error}",
                recipient_id=recipient_id,
                error=str(exc),
            )
            raise NotificationPermanentError(message="Permanent Telegram delivery failure") from exc
        except TelegramAPIError as exc:
            logger.warning(
                "Telegram API error while sending message | recipient_id={recipient_id} error={error}",
                recipient_id=recipient_id,
                error=str(exc),
            )
            raise NotificationPermanentError(message="Telegram API delivery failure") from exc
        except Exception as exc:
            logger.exception(
                "Failed to send direct notification | recipient_id={recipient_id} message_preview={message_preview}",
                recipient_id=recipient_id,
                message_preview=cleaned_text[:120],
            )
            raise NotificationPermanentError(message="Unexpected notification delivery failure") from exc
