from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from unittest.mock import AsyncMock

import pytest
from aiogram.types import Chat, Message, User

from pybot.bot.handlers.roles.change_roles import _extract_role_and_reason, handle_set_role
from pybot.core.constants import RoleEnum


def _build_message(*, text: str, from_user_id: int = 710_001) -> Message:
    sender = User(id=from_user_id, is_bot=False, first_name="Admin")
    return Message(
        message_id=1,
        date=datetime.now(UTC),
        chat=Chat(id=from_user_id, type="private"),
        from_user=sender,
        text=text,
    )


@dataclass(slots=True)
class StubUserService:
    add_user_role: AsyncMock = field(default_factory=AsyncMock)


def _last_reply_text(reply_mock: AsyncMock) -> str:
    assert reply_mock.await_args_list
    return str(reply_mock.await_args_list[-1].args[0])


@pytest.mark.asyncio
async def test_extract_role_and_reason_parses_quoted_reason(monkeypatch: pytest.MonkeyPatch) -> None:
    # Given
    message = _build_message(text='/addrole @mentor Admin "For great mentoring"')
    reply_mock = AsyncMock()
    monkeypatch.setattr(Message, "reply", reply_mock)

    # When
    role, reason = await _extract_role_and_reason(message)

    # Then
    assert role is RoleEnum.ADMIN
    assert reason == "For great mentoring"
    reply_mock.assert_not_awaited()


@pytest.mark.asyncio
async def test_extract_role_and_reason_accepts_command_without_reason(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    # Given
    message = _build_message(text="/addrole Admin")
    reply_mock = AsyncMock()
    monkeypatch.setattr(Message, "reply", reply_mock)

    # When
    role, reason = await _extract_role_and_reason(message)

    # Then
    assert role is RoleEnum.ADMIN
    assert reason is None
    reply_mock.assert_not_awaited()


@pytest.mark.asyncio
async def test_extract_role_and_reason_rejects_unquoted_reason(monkeypatch: pytest.MonkeyPatch) -> None:
    # Given
    message = _build_message(text="/addrole Admin because we need help")
    reply_mock = AsyncMock()
    monkeypatch.setattr(Message, "reply", reply_mock)

    # When
    role, reason = await _extract_role_and_reason(message)

    # Then
    assert role is None
    assert reason is None
    reply_mock.assert_awaited_once()
    assert '"' in _last_reply_text(reply_mock) or "'" in _last_reply_text(reply_mock)


@pytest.mark.asyncio
async def test_handle_set_role_explains_how_to_select_target_user(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    # Given
    message = _build_message(text="/addrole Admin")
    user_service = StubUserService()
    reply_mock = AsyncMock()
    monkeypatch.setattr(Message, "reply", reply_mock)

    # When
    await handle_set_role(message=message, user_service=user_service, user_id=999_999)

    # Then
    user_service.add_user_role.assert_not_awaited()
    reply_mock.assert_awaited_once()
    assert "/setrole" in _last_reply_text(reply_mock)
