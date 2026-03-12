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

from ...bot.keyboards.role_request_keyboard import get_admin_decision_kb
from ...core import logger
from ...core.config import settings
from ...dto import NotifyDTO
from ...services.ports import NotificationPermanentError, NotificationPort, NotificationTemporaryError


class TelegramNotificationService(NotificationPort):
    """Telegram implementation of :class:`NotificationPort`.

    Notes:
        ``user_id`` in this adapter is interpreted as Telegram ``telegram_id``.
    """

    def __init__(self, bot: Bot) -> None:
        """Initialize Telegram notification adapter.

        Args:
            bot: Shared aiogram bot instance.
        """
        self.bot = bot

    async def send_role_request_to_admin(self, request_id: int, requester_user_id: int, role_name: str) -> None:
        """Send role request details to configured Telegram admin.

        Args:
            request_id: Role request identifier.
            requester_user_id: Requester Telegram ``telegram_id``.
            role_name: Requested role name.

        Raises:
            NotificationTemporaryError: Transient Telegram delivery failure.
            NotificationPermanentError: Non-retryable Telegram delivery failure.
        """
        admin_tg_id = settings.role_request_admin_tg_id

        mention = f"<a href='tg://user?id={requester_user_id}'>user {requester_user_id}</a>"
        text = f"Новый запрос роли\n\nRequest ID: {request_id}\nРоль: {role_name}\nПользователь: {mention}"

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
        """Send a direct Telegram message.

        Args:
            message_data: Validated direct-notification payload.

        Raises:
            NotificationTemporaryError: Transient Telegram delivery failure.
            NotificationPermanentError: Non-retryable Telegram delivery failure.
        """
        try:
            cleaned_text, user_id = message_data.message, message_data.user_id
            await self.bot.send_message(chat_id=user_id, text=cleaned_text)
        except TelegramRetryAfter as exc:
            logger.warning(
                "Telegram retry-after while sending message | user_id={user_id} retry_after={retry_after}",
                user_id=user_id,
                retry_after=exc.retry_after,
            )
            raise NotificationTemporaryError(
                message="Telegram rate limit encountered",
                retry_after_seconds=float(exc.retry_after),
            ) from exc
        except (TelegramNetworkError, TelegramServerError, RestartingTelegram) as exc:
            logger.warning(
                "Temporary Telegram failure while sending message | user_id={user_id} error={error}",
                user_id=user_id,
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
                user_id=user_id,
                error=str(exc),
            )
            raise NotificationPermanentError(message="Permanent Telegram delivery failure") from exc
        except TelegramAPIError as exc:
            logger.warning(
                "Telegram API error while sending message | user_id={user_id} error={error}",
                user_id=user_id,
                error=str(exc),
            )
            raise NotificationPermanentError(message="Telegram API delivery failure") from exc
        except Exception as exc:
            logger.exception(
                "Failed to send direct notification | user_id={user_id} message_preview={message_preview}",
                user_id=user_id,
                message_preview=cleaned_text[:120],
            )
            raise NotificationPermanentError(message="Unexpected notification delivery failure") from exc
