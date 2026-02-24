from abc import ABC, abstractmethod

from ...core.constants import RoleEnum


class NotificationPort(ABC):
    @abstractmethod
    async def send_role_request_to_admin(self, request_id: int) -> None:
        pass

    @abstractmethod
    async def send_message(self, user_id: int, message_text: str) -> None:
        pass

    @abstractmethod
    async def broadcast(self, message_text: str, selected_role: RoleEnum | None) -> None:
        pass
