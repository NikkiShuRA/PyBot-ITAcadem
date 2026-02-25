from typing import Any, Protocol, runtime_checkable

from aiogram import Bot

from ...bot.keyboards.role_request_keyboard import get_admin_decision_kb
from ...core import logger
from ...core.config import settings
from ...core.constants import RoleEnum
from ...services.ports import NotificationPort


@runtime_checkable
class TelegramBotProtocol(Protocol):
    async def send_message(self, *args: Any, **kwargs: Any) -> Any:
        pass


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
        self.bot: TelegramBotProtocol = bot

    async def send_role_request_to_admin(self, request_id: int, requester_user_id: int, role_name: str) -> None:
        """Send role request details to configured Telegram admin.

        Args:
            request_id: Role request identifier.
            requester_user_id: Requester Telegram ``telegram_id``.
            role_name: Requested role name.

        Raises:
            ValueError: If admin Telegram id is not configured.
            Exception: Any Telegram API error is re-raised after logging.
        """
        admin_tg_id = settings.role_request_admin_tg_id
        if admin_tg_id <= 0:  # TODO Убрать если поставиться обязательное id для админа
            logger.error(
                "Invalid ROLE_REQUEST_ADMIN_TG_ID configuration: {admin_tg_id}",
                admin_tg_id=admin_tg_id,
            )
            raise ValueError("ROLE_REQUEST_ADMIN_TG_ID must be configured and greater than 0")

        mention = f"<a href='tg://user?id={requester_user_id}'>user {requester_user_id}</a>"
        text = f"Новый запрос роли\n\nRequest ID: {request_id}\nРоль: {role_name}\nПользователь: {mention}"

        try:
            await self.bot.send_message(
                chat_id=admin_tg_id,
                text=text,
                parse_mode="HTML",
                reply_markup=get_admin_decision_kb(request_id),
            )
        except Exception:
            logger.exception(
                "Failed to send role request notification | "
                "admin_tg_id={admin_tg_id} request_id={request_id} "
                "requester_user_id={requester_user_id} role_name={role_name}",
                admin_tg_id=admin_tg_id,
                request_id=request_id,
                requester_user_id=requester_user_id,
                role_name=role_name,
            )
            raise

    async def send_message(self, user_id: int, message_text: str) -> None:
        """Send a direct Telegram message.

        Args:
            user_id: Recipient Telegram ``telegram_id``.
            message_text: Outgoing message text.

        Raises:
            ValueError: If user id is invalid or text is blank.
            Exception: Any Telegram API error is re-raised after logging.
        """
        if user_id <= 0:
            raise ValueError("user_id must be greater than 0")

        cleaned_text = message_text.strip()
        if not cleaned_text:
            raise ValueError("message_text must not be empty")

        try:
            await self.bot.send_message(chat_id=user_id, text=cleaned_text)
        except Exception:
            logger.exception(
                "Failed to send direct notification | user_id={user_id} message_preview={message_preview}",
                user_id=user_id,
                message_preview=cleaned_text[:120],
            )
            raise

    async def broadcast(self, message_text: str, selected_role: RoleEnum | None) -> None:
        """Broadcast message via Telegram transport.

        Args:
            message_text: Outgoing message text.
            selected_role: Optional role filter. ``None`` means all users.

        Raises:
            NotImplementedError: Broadcast is out of current task scope.
        """
        raise NotImplementedError("Broadcast is not implemented in current task")
