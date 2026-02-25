from __future__ import annotations

from typing import Any

from aiogram import Bot
from dishka import Provider, Scope, provide

from pybot.core.constants import RoleEnum
from pybot.services.ports import NotificationPort

__test__ = False


class FakeNotificationPort(NotificationPort):
    """In-memory notification adapter for isolated tests."""

    def __init__(self) -> None:
        self.role_requests: list[dict[str, Any]] = []
        self.direct_messages: list[dict[str, Any]] = []
        self.broadcast_messages: list[dict[str, Any]] = []

    async def send_role_request_to_admin(self, request_id: int, requester_user_id: int, role_name: str) -> None:
        self.role_requests.append(
            {
                "request_id": request_id,
                "requester_user_id": requester_user_id,
                "role_name": role_name,
            }
        )

    async def send_message(self, user_id: int, message_text: str) -> None:
        self.direct_messages.append(
            {
                "user_id": user_id,
                "message_text": message_text,
            }
        )

    async def broadcast(self, message_text: str, selected_role: RoleEnum | None) -> None:
        self.broadcast_messages.append(
            {
                "message_text": message_text,
                "selected_role": selected_role,
            }
        )


class FakeBot:
    """Minimal bot stub to avoid real Telegram API calls in tests."""

    def __init__(self) -> None:
        self.sent_messages: list[dict[str, Any]] = []

    async def send_message(self, *args: Any, **kwargs: Any) -> None:
        self.sent_messages.append(
            {
                "args": args,
                "kwargs": kwargs,
            }
        )


class TestOverridesProvider(Provider):
    """Dishka provider with fake outbound adapters for tests."""

    def __init__(self) -> None:
        super().__init__()
        self._fake_bot = FakeBot()
        self._notification_port = FakeNotificationPort()

    @provide(scope=Scope.APP)
    def provide_bot(self) -> Bot:
        return self._fake_bot  # type: ignore[return-value]

    @provide(scope=Scope.APP)
    def provide_notification_port(self) -> NotificationPort:
        return self._notification_port

    @provide(scope=Scope.APP)
    def provide_fake_notification_port(self) -> FakeNotificationPort:
        return self._notification_port
