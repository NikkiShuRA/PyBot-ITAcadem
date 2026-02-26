from __future__ import annotations

from dataclasses import dataclass

from aiogram.types import InlineKeyboardMarkup
from dishka import Provider, Scope, provide

from pybot.services.ports import NotificationPort

__test__ = False


class FakeNotificationPort(NotificationPort):
    """In-memory notification adapter for isolated tests."""

    def __init__(self) -> None:
        self.role_requests: list[RoleRequestNotificationRecord] = []
        self.direct_messages: list[DirectMessageNotificationRecord] = []

    async def send_role_request_to_admin(self, request_id: int, requester_user_id: int, role_name: str) -> None:
        self.role_requests.append(
            RoleRequestNotificationRecord(
                request_id=request_id,
                requester_user_id=requester_user_id,
                role_name=role_name,
            )
        )

    async def send_message(self, user_id: int, message_text: str) -> None:
        self.direct_messages.append(
            DirectMessageNotificationRecord(
                user_id=user_id,
                message_text=message_text,
            )
        )


@dataclass(frozen=True, slots=True)
class RoleRequestNotificationRecord:
    request_id: int
    requester_user_id: int
    role_name: str


@dataclass(frozen=True, slots=True)
class DirectMessageNotificationRecord:
    user_id: int
    message_text: str


@dataclass(frozen=True, slots=True)
class SentMessageRecord:
    chat_id: int
    text: str
    parse_mode: str | None
    reply_markup: InlineKeyboardMarkup | None


class FakeBot:
    """Minimal bot stub to avoid real Telegram API calls in tests."""

    def __init__(self) -> None:
        self.sent_messages: list[SentMessageRecord] = []

    async def send_message(
        self,
        chat_id: int,
        text: str,
        parse_mode: str | None = None,
        reply_markup: InlineKeyboardMarkup | None = None,
    ) -> None:
        self.sent_messages.append(
            SentMessageRecord(
                chat_id=chat_id,
                text=text,
                parse_mode=parse_mode,
                reply_markup=reply_markup,
            )
        )


class TestOverridesProvider(Provider):
    """Dishka provider with fake outbound adapters for tests."""

    def __init__(self) -> None:
        super().__init__()
        self._fake_bot = FakeBot()
        self._notification_port = FakeNotificationPort()

    @provide(scope=Scope.APP)
    def provide_bot(self) -> FakeBot:
        return self._fake_bot

    @provide(scope=Scope.APP)
    def provide_notification_port(self) -> NotificationPort:
        return self._notification_port

    @provide(scope=Scope.APP)
    def provide_fake_notification_port(self) -> FakeNotificationPort:
        return self._notification_port
