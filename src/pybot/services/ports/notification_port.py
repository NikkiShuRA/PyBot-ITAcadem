from abc import ABC, abstractmethod

from ...core.constants import RoleEnum


class NotificationPort(ABC):
    """Outbound notifications contract for application services.

    Notes:
        The semantic meaning of ``user_id`` depends on a concrete transport
        implementation. For Telegram-based implementations, ``user_id`` maps to
        Telegram ``telegram_id``.
    """

    @abstractmethod
    async def send_role_request_to_admin(
        self,
        request_id: int,
        requester_user_id: int,
        role_name: str,
    ) -> None:
        """Send a role request notification to the administrator.

        Args:
            request_id: Unique role-request identifier.
            requester_user_id: Requester identifier in current notification
                transport semantics.
            role_name: Requested role name.
        """
        pass

    @abstractmethod
    async def send_message(self, user_id: int, message_text: str) -> None:
        """Send a direct message to a single recipient.

        Args:
            user_id: Recipient identifier in current notification transport
                semantics.
            message_text: Notification text.
        """
        pass

    @abstractmethod
    async def broadcast(self, message_text: str, selected_role: RoleEnum | None) -> None:
        """Broadcast a message to a role segment or all users.

        Args:
            message_text: Notification text.
            selected_role: Optional role filter. ``None`` means all users.
        """
        pass
