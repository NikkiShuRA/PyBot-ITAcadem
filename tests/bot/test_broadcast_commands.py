from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from unittest.mock import AsyncMock

import pytest
from aiogram.types import Chat, Message, User

from pybot.bot.handlers.broadcast.broadcast_commands import (
    _extract_message_for_broadcast,
    broadcast_command,
)
from pybot.domain.exceptions import BroadcastMessageNotSpecifiedError
from pybot.dto import CompetenceReadDTO


def _build_message(text: str, user_id: int = 100_001) -> Message:
    sender = User(id=user_id, is_bot=False, first_name="Admin")
    return Message(
        message_id=1,
        date=datetime.now(UTC),
        chat=Chat(id=user_id, type="private"),
        from_user=sender,
        text=text,
    )


@dataclass(slots=True)
class StubBroadcastService:
    all_messages: list[str] = field(default_factory=list)
    role_messages: list[tuple[str, str]] = field(default_factory=list)
    competence_messages: list[tuple[int, str]] = field(default_factory=list)

    async def broadcast_for_all(self, message: str) -> None:
        self.all_messages.append(message)

    async def broadcast_for_users_with_role(self, role_name: str, message: str) -> None:
        self.role_messages.append((role_name, message))

    async def broadcast_for_users_with_competence(self, competence_id: int, message: str) -> None:
        self.competence_messages.append((competence_id, message))


@dataclass(slots=True)
class StubCompetenceService:
    competencies: list[CompetenceReadDTO]

    async def get_all_competencies(self) -> list[CompetenceReadDTO]:
        return self.competencies


def _last_reply_text(reply_mock: AsyncMock) -> str:
    assert reply_mock.await_args_list
    return str(reply_mock.await_args_list[-1][0][0])


@pytest.mark.asyncio
async def test_extract_message_for_broadcast_after_competence_target() -> None:
    message = _build_message("/broadcast Python hello team")
    extracted = await _extract_message_for_broadcast(message, "Python")
    assert extracted == "hello team"


@pytest.mark.asyncio
async def test_extract_message_for_broadcast_raises_when_message_is_missing() -> None:
    message = _build_message("/broadcast @all")
    with pytest.raises(BroadcastMessageNotSpecifiedError):
        await _extract_message_for_broadcast(message, "@all")


@pytest.mark.asyncio
async def test_broadcast_command_routes_to_all(monkeypatch: pytest.MonkeyPatch) -> None:
    message = _build_message("/broadcast @all hello everyone")
    broadcast_service = StubBroadcastService()
    competence_service = StubCompetenceService(competencies=[])
    reply_mock = AsyncMock()
    monkeypatch.setattr(Message, "reply", reply_mock)

    await broadcast_command(
        message=message,
        broadcast_service=broadcast_service,
        competence_service=competence_service,
    )

    assert broadcast_service.all_messages == ["hello everyone"]
    assert broadcast_service.role_messages == []
    assert broadcast_service.competence_messages == []
    assert reply_mock.await_count == 0


@pytest.mark.asyncio
async def test_broadcast_command_routes_to_role(monkeypatch: pytest.MonkeyPatch) -> None:
    message = _build_message("/broadcast Admin hello role")
    broadcast_service = StubBroadcastService()
    competence_service = StubCompetenceService(competencies=[])
    reply_mock = AsyncMock()
    monkeypatch.setattr(Message, "reply", reply_mock)

    await broadcast_command(
        message=message,
        broadcast_service=broadcast_service,
        competence_service=competence_service,
    )

    assert broadcast_service.all_messages == []
    assert broadcast_service.role_messages == [("Admin", "hello role")]
    assert broadcast_service.competence_messages == []
    assert reply_mock.await_count == 0


@pytest.mark.asyncio
async def test_broadcast_command_routes_to_competence(monkeypatch: pytest.MonkeyPatch) -> None:
    message = _build_message("/broadcast Python hello competence")
    broadcast_service = StubBroadcastService()
    competence_service = StubCompetenceService(
        competencies=[
            CompetenceReadDTO(id=1, name="Python", description=None),
            CompetenceReadDTO(id=2, name="SQL", description=None),
        ]
    )
    reply_mock = AsyncMock()
    monkeypatch.setattr(Message, "reply", reply_mock)

    await broadcast_command(
        message=message,
        broadcast_service=broadcast_service,
        competence_service=competence_service,
    )

    assert broadcast_service.all_messages == []
    assert broadcast_service.role_messages == []
    assert broadcast_service.competence_messages == [(1, "hello competence")]
    assert reply_mock.await_count == 0


@pytest.mark.asyncio
async def test_broadcast_command_replies_when_target_is_unknown(monkeypatch: pytest.MonkeyPatch) -> None:
    message = _build_message("/broadcast Unknown hello")
    broadcast_service = StubBroadcastService()
    competence_service = StubCompetenceService(competencies=[CompetenceReadDTO(id=1, name="Python", description=None)])
    reply_mock = AsyncMock()
    monkeypatch.setattr(Message, "reply", reply_mock)

    await broadcast_command(
        message=message,
        broadcast_service=broadcast_service,
        competence_service=competence_service,
    )

    assert broadcast_service.all_messages == []
    assert broadcast_service.role_messages == []
    assert broadcast_service.competence_messages == []
    assert reply_mock.await_count == 1
    assert "Unknown broadcast target" in _last_reply_text(reply_mock)


@pytest.mark.asyncio
async def test_broadcast_command_replies_when_broadcast_message_missing(monkeypatch: pytest.MonkeyPatch) -> None:
    message = _build_message("/broadcast @all")
    broadcast_service = StubBroadcastService()
    competence_service = StubCompetenceService(competencies=[])
    reply_mock = AsyncMock()
    monkeypatch.setattr(Message, "reply", reply_mock)

    await broadcast_command(
        message=message,
        broadcast_service=broadcast_service,
        competence_service=competence_service,
    )

    assert broadcast_service.all_messages == []
    assert broadcast_service.role_messages == []
    assert broadcast_service.competence_messages == []
    assert reply_mock.await_count == 1
    assert "Broadcast message is required" in _last_reply_text(reply_mock)
