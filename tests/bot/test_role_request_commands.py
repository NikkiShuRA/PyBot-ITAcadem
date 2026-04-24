from __future__ import annotations

from datetime import UTC, datetime
from unittest.mock import AsyncMock

import pytest
from aiogram.types import Chat, Message, User

from pybot.bot.handlers.roles.role_request_flow import cmd_role_request
from pybot.presentation.texts import ROLE_REQUEST_USAGE, role_request_cooldown_until
from pybot.domain.exceptions import RoleRequestCooldownError


def _build_message(
    *,
    text: str,
    from_user_id: int = 930_001,
    date: datetime | None = None,
) -> Message:
    sender = User(id=from_user_id, is_bot=False, first_name="Student")
    return Message(
        message_id=1,
        date=date or datetime.now(UTC),
        chat=Chat(id=from_user_id, type="private"),
        from_user=sender,
        text=text,
    )


@pytest.mark.asyncio
async def test_cmd_role_request_replies_with_relative_cooldown_for_next_day(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    request_time = datetime(2026, 3, 22, 14, 30, 0, tzinfo=UTC)
    available_at = datetime(2026, 3, 23, 14, 30, 0)
    role_request_service = AsyncMock()
    role_request_service.create_role_request.side_effect = RoleRequestCooldownError(
        user_id=1,
        role_name="Mentor",
        available_at=available_at,
    )

    message = _build_message(text="/role_request Mentor", date=request_time)
    reply_mock = AsyncMock()
    monkeypatch.setattr(Message, "reply", reply_mock)

    await cmd_role_request(
        message=message,
        role_request_service=role_request_service,
        user_id=1,
    )

    role_request_service.create_role_request.assert_awaited_once_with(1, "Mentor")
    reply_mock.assert_awaited_once_with(role_request_cooldown_until("завтра в 14:30 (через 1 день)"))


@pytest.mark.asyncio
async def test_cmd_role_request_replies_with_absolute_cooldown_for_longer_wait(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    request_time = datetime(2026, 3, 22, 12, 0, 0, tzinfo=UTC)
    available_at = datetime(2026, 3, 24, 14, 30, 0)
    role_request_service = AsyncMock()
    role_request_service.create_role_request.side_effect = RoleRequestCooldownError(
        user_id=1,
        role_name="Mentor",
        available_at=available_at,
    )

    message = _build_message(text="/role_request Mentor", date=request_time)
    reply_mock = AsyncMock()
    monkeypatch.setattr(Message, "reply", reply_mock)

    await cmd_role_request(
        message=message,
        role_request_service=role_request_service,
        user_id=1,
    )

    role_request_service.create_role_request.assert_awaited_once_with(1, "Mentor")
    reply_mock.assert_awaited_once_with(
        role_request_cooldown_until("24 марта 2026 в 14:30 (через 2 дня 2 часа 30 минут)")
    )


@pytest.mark.asyncio
async def test_cmd_role_request_explains_correct_format_for_unknown_role(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    role_request_service = AsyncMock()
    message = _build_message(text="/role_request Curator")
    reply_mock = AsyncMock()
    monkeypatch.setattr(Message, "reply", reply_mock)

    await cmd_role_request(
        message=message,
        role_request_service=role_request_service,
        user_id=1,
    )

    role_request_service.create_role_request.assert_not_awaited()
    reply_mock.assert_awaited_once_with(ROLE_REQUEST_USAGE)
