from __future__ import annotations

import asyncio
from collections import defaultdict, deque
from collections.abc import Sequence
from dataclasses import dataclass
from enum import Enum
from unittest.mock import AsyncMock

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from pybot.core.config import settings
from pybot.db.models import User
from pybot.infrastructure.user_repository import UserRepository
from pybot.services.broadcast import BroadcastAlreadyRunningError, BroadcastService
from pybot.services.ports import NotificationPermanentError, NotificationPort, NotificationTemporaryError


class DeliveryOutcome(Enum):
    OK = "ok"
    TEMPORARY = "temporary"
    PERMANENT = "permanent"
    UNEXPECTED = "unexpected"


@dataclass(slots=True)
class FakeUserRepository(UserRepository):
    users: list[User]
    role_users: dict[str, list[User]]

    async def get_all_users(self, db: AsyncSession) -> Sequence[User]:
        return self.users

    async def get_all_users_with_role(self, db: AsyncSession, role_name: str) -> Sequence[User]:
        return self.role_users.get(role_name, [])


class ScriptedNotificationPort(NotificationPort):
    def __init__(
        self,
        plans: dict[int, list[DeliveryOutcome]] | None = None,
        started_event: asyncio.Event | None = None,
        release_event: asyncio.Event | None = None,
    ) -> None:
        self._plans: dict[int, deque[DeliveryOutcome]] = {
            user_id: deque(outcomes) for user_id, outcomes in (plans or {}).items()
        }
        self.started_event = started_event
        self.release_event = release_event
        self.call_counts: dict[int, int] = defaultdict(int)

    async def send_role_request_to_admin(self, request_id: int, requester_user_id: int, role_name: str) -> None:
        return None

    async def send_message(self, user_id: int, message_text: str) -> None:
        self.call_counts[user_id] += 1

        if self.started_event is not None and not self.started_event.is_set():
            self.started_event.set()
        if self.release_event is not None:
            await self.release_event.wait()

        outcomes = self._plans.get(user_id)
        outcome = outcomes.popleft() if outcomes else DeliveryOutcome.OK

        if outcome is DeliveryOutcome.TEMPORARY:
            raise NotificationTemporaryError("temporary failure", retry_after_seconds=0.0)
        if outcome is DeliveryOutcome.PERMANENT:
            raise NotificationPermanentError("permanent failure")
        if outcome is DeliveryOutcome.UNEXPECTED:
            raise RuntimeError("unexpected failure")


def _mk_user(telegram_id: int) -> User:
    return User(first_name=f"user-{telegram_id}", telegram_id=telegram_id)


def _configure_broadcast_settings(
    monkeypatch: pytest.MonkeyPatch,
    *,
    bulk_size: int = 20,
    max_concurrency: int = 5,
    batch_pause_ms: int = 1200,
    jitter_min_ms: int = 80,
    jitter_max_ms: int = 160,
    retry_attempts: int = 5,
    retry_max_wait_s: int = 1,
) -> None:
    monkeypatch.setattr(settings, "broadcast_bulk_size", bulk_size)
    monkeypatch.setattr(settings, "broadcast_max_concurrency", max_concurrency)
    monkeypatch.setattr(settings, "broadcast_batch_pause_ms", batch_pause_ms)
    monkeypatch.setattr(settings, "broadcast_jitter_min_ms", jitter_min_ms)
    monkeypatch.setattr(settings, "broadcast_jitter_max_ms", jitter_max_ms)
    monkeypatch.setattr(settings, "broadcast_retry_attempts", retry_attempts)
    monkeypatch.setattr(settings, "broadcast_retry_max_wait_s", retry_max_wait_s)


@pytest.mark.asyncio
async def test_broadcast_for_all_happy_path(monkeypatch: pytest.MonkeyPatch) -> None:
    _configure_broadcast_settings(monkeypatch, bulk_size=2, max_concurrency=2, jitter_min_ms=80, jitter_max_ms=80)
    users = [_mk_user(1), _mk_user(2), _mk_user(3)]
    user_repository = FakeUserRepository(users=users, role_users={})
    notification_port = ScriptedNotificationPort()
    service = BroadcastService(AsyncMock(spec=AsyncSession), user_repository, notification_port)

    sleep_mock = AsyncMock()
    monkeypatch.setattr(asyncio, "sleep", sleep_mock)

    result = await service.broadcast_for_all("hello")

    assert result.attempted == 3
    assert result.sent == 3
    assert result.failed_temporary == 0
    assert result.failed_permanent == 0
    assert result.skipped_invalid_user == 0
    sleep_mock.assert_awaited_once_with(1.28)


@pytest.mark.asyncio
async def test_broadcast_for_all_handles_partial_permanent_failure(monkeypatch: pytest.MonkeyPatch) -> None:
    _configure_broadcast_settings(monkeypatch, bulk_size=3, max_concurrency=3, retry_attempts=2)
    users = [_mk_user(10), _mk_user(20), _mk_user(30)]
    user_repository = FakeUserRepository(users=users, role_users={})
    notification_port = ScriptedNotificationPort(
        plans={
            20: [DeliveryOutcome.PERMANENT],
        }
    )
    service = BroadcastService(AsyncMock(spec=AsyncSession), user_repository, notification_port)

    result = await service.broadcast_for_all("hello")

    assert result.attempted == 3
    assert result.sent == 2
    assert result.failed_temporary == 0
    assert result.failed_permanent == 1


@pytest.mark.asyncio
async def test_broadcast_for_all_retries_temporary_then_succeeds(monkeypatch: pytest.MonkeyPatch) -> None:
    _configure_broadcast_settings(monkeypatch, retry_attempts=3, retry_max_wait_s=1)
    users = [_mk_user(100)]
    user_repository = FakeUserRepository(users=users, role_users={})
    notification_port = ScriptedNotificationPort(
        plans={
            100: [DeliveryOutcome.TEMPORARY, DeliveryOutcome.OK],
        }
    )
    service = BroadcastService(AsyncMock(spec=AsyncSession), user_repository, notification_port)

    sleep_mock = AsyncMock()
    monkeypatch.setattr(asyncio, "sleep", sleep_mock)

    result = await service.broadcast_for_all("hello")

    assert result.sent == 1
    assert result.failed_temporary == 0
    assert notification_port.call_counts[100] == 2


@pytest.mark.asyncio
async def test_broadcast_for_all_marks_temporary_failure_when_retry_exhausted(monkeypatch: pytest.MonkeyPatch) -> None:
    _configure_broadcast_settings(monkeypatch, retry_attempts=2, retry_max_wait_s=1)
    users = [_mk_user(200)]
    user_repository = FakeUserRepository(users=users, role_users={})
    notification_port = ScriptedNotificationPort(
        plans={
            200: [DeliveryOutcome.TEMPORARY, DeliveryOutcome.TEMPORARY, DeliveryOutcome.OK],
        }
    )
    service = BroadcastService(AsyncMock(spec=AsyncSession), user_repository, notification_port)

    result = await service.broadcast_for_all("hello")

    assert result.sent == 0
    assert result.failed_temporary == 1
    assert result.failed_permanent == 0
    assert notification_port.call_counts[200] == 2


@pytest.mark.asyncio
async def test_broadcast_for_all_raises_when_already_running(monkeypatch: pytest.MonkeyPatch) -> None:
    _configure_broadcast_settings(monkeypatch, retry_attempts=1)
    users = [_mk_user(300)]
    user_repository = FakeUserRepository(users=users, role_users={})
    started_event = asyncio.Event()
    release_event = asyncio.Event()
    notification_port = ScriptedNotificationPort(started_event=started_event, release_event=release_event)
    service = BroadcastService(AsyncMock(spec=AsyncSession), user_repository, notification_port)

    first_task = asyncio.create_task(service.broadcast_for_all("hello"))
    await started_event.wait()

    with pytest.raises(BroadcastAlreadyRunningError):
        await service.broadcast_for_all("hello")

    release_event.set()
    await first_task


@pytest.mark.asyncio
async def test_broadcast_validates_message(monkeypatch: pytest.MonkeyPatch) -> None:
    _configure_broadcast_settings(monkeypatch)
    user_repository = FakeUserRepository(users=[_mk_user(1)], role_users={})
    notification_port = ScriptedNotificationPort()
    service = BroadcastService(AsyncMock(spec=AsyncSession), user_repository, notification_port)

    with pytest.raises(ValueError, match="message"):
        await service.broadcast_for_all("   ")


@pytest.mark.asyncio
async def test_broadcast_for_users_with_role_validates_role_name(monkeypatch: pytest.MonkeyPatch) -> None:
    _configure_broadcast_settings(monkeypatch)
    user_repository = FakeUserRepository(users=[], role_users={})
    notification_port = ScriptedNotificationPort()
    service = BroadcastService(AsyncMock(spec=AsyncSession), user_repository, notification_port)

    with pytest.raises(ValueError, match="role_name"):
        await service.broadcast_for_users_with_role("  ", "hello")
