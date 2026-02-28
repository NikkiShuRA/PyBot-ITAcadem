from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass, field
from datetime import UTC, date, datetime
from unittest.mock import AsyncMock

import pytest
from aiogram.types import Chat, Message, User

from pybot.bot.handlers.roles.change_competences import (
    handle_add_competence,
    handle_remove_competence,
    handle_show_competences,
)
from pybot.core.constants import LevelTypeEnum
from pybot.dto import CompetenceReadDTO, UserReadDTO
from pybot.dto.value_objects import Points


def _build_user_read_dto(db_id: int, telegram_id: int, first_name: str) -> UserReadDTO:
    return UserReadDTO(
        id=db_id,
        first_name=first_name,
        last_name="Test",
        patronymic=None,
        telegram_id=telegram_id,
        academic_points=Points(value=0, point_type=LevelTypeEnum.ACADEMIC),
        reputation_points=Points(value=0, point_type=LevelTypeEnum.REPUTATION),
        join_date=date.today(),
    )


def _build_message(
    *,
    text: str,
    from_user_id: int,
    reply_user_id: int | None = None,
) -> Message:
    sender = User(id=from_user_id, is_bot=False, first_name="Admin")
    reply_message: Message | None = None

    if reply_user_id is not None:
        target_user = User(id=reply_user_id, is_bot=False, first_name="Target")
        reply_message = Message(
            message_id=99,
            date=datetime.now(UTC),
            chat=Chat(id=from_user_id, type="private"),
            from_user=target_user,
            text="target",
        )

    return Message(
        message_id=1,
        date=datetime.now(UTC),
        chat=Chat(id=from_user_id, type="private"),
        from_user=sender,
        text=text,
        reply_to_message=reply_message,
    )


@dataclass(slots=True)
class StubUserService:
    users_by_tg: dict[int, UserReadDTO] = field(default_factory=dict)
    users_by_id: dict[int, UserReadDTO] = field(default_factory=dict)
    competencies_by_user_id: dict[int, list[CompetenceReadDTO]] = field(default_factory=dict)
    add_calls: list[tuple[int, list[str]]] = field(default_factory=list)
    remove_calls: list[tuple[int, list[str]]] = field(default_factory=list)
    show_calls: list[int] = field(default_factory=list)
    add_error: ValueError | None = None
    remove_error: ValueError | None = None

    async def get_user_by_telegram_id(self, tg_id: int) -> UserReadDTO | None:
        return self.users_by_tg.get(tg_id)

    async def get_user(self, user_id: int) -> UserReadDTO | None:
        return self.users_by_id.get(user_id)

    async def add_user_competencies_by_names(self, user_id: int, competence_names: Sequence[str]) -> UserReadDTO:
        self.add_calls.append((user_id, list(competence_names)))
        if self.add_error is not None:
            raise self.add_error
        user = self.users_by_id.get(user_id)
        if user is None:
            raise ValueError("User not found")
        return user

    async def remove_user_competencies_by_names(self, user_id: int, competence_names: Sequence[str]) -> UserReadDTO:
        self.remove_calls.append((user_id, list(competence_names)))
        if self.remove_error is not None:
            raise self.remove_error
        user = self.users_by_id.get(user_id)
        if user is None:
            raise ValueError("User not found")
        return user

    async def get_user_competencies(self, user_id: int) -> Sequence[CompetenceReadDTO]:
        self.show_calls.append(user_id)
        return self.competencies_by_user_id.get(user_id, [])


def _last_reply_text(reply_mock: AsyncMock) -> str:
    assert reply_mock.await_args_list
    return str(reply_mock.await_args_list[-1][0][0])


@pytest.mark.asyncio
async def test_addcompetence_by_reply_calls_service_with_csv_names(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    target_user = _build_user_read_dto(db_id=20, telegram_id=200_001, first_name="Target")
    service = StubUserService(
        users_by_tg={target_user.telegram_id: target_user},
        users_by_id={target_user.id: target_user},
    )
    message = _build_message(
        text="/addcompetence Python, SQL",
        from_user_id=100_001,
        reply_user_id=target_user.telegram_id,
    )

    reply_mock = AsyncMock()
    monkeypatch.setattr(Message, "reply", reply_mock)

    await handle_add_competence(message=message, user_service=service)

    assert service.add_calls == [(target_user.id, ["Python", "SQL"])]
    assert reply_mock.await_count == 1
    reply_text = _last_reply_text(reply_mock)
    assert "Python" in reply_text
    assert "SQL" in reply_text


@pytest.mark.asyncio
async def test_removecompetence_invalid_list_returns_error_message(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    target_user = _build_user_read_dto(db_id=21, telegram_id=200_002, first_name="Target")
    service = StubUserService(
        users_by_tg={target_user.telegram_id: target_user},
        users_by_id={target_user.id: target_user},
        remove_error=ValueError("Competence names not found: ['Unknown']"),
    )
    message = _build_message(text="/removecompetence 200002 Unknown", from_user_id=100_002)

    reply_mock = AsyncMock()
    monkeypatch.setattr(Message, "reply", reply_mock)

    await handle_remove_competence(message=message, user_service=service)

    assert service.remove_calls == [(target_user.id, ["Unknown"])]
    assert "Competence names not found" in _last_reply_text(reply_mock)


@pytest.mark.asyncio
async def test_showcompetences_without_target_uses_current_user(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    current_user = _build_user_read_dto(db_id=30, telegram_id=300_001, first_name="Admin")
    service = StubUserService(
        users_by_id={current_user.id: current_user},
        competencies_by_user_id={
            current_user.id: [CompetenceReadDTO(id=1, name="Python", description=None)],
        },
    )
    message = _build_message(text="/showcompetences", from_user_id=current_user.telegram_id)

    reply_mock = AsyncMock()
    monkeypatch.setattr(Message, "reply", reply_mock)

    await handle_show_competences(message=message, user_service=service, user_id=current_user.id)

    assert service.show_calls == [current_user.id]
    assert "Python" in _last_reply_text(reply_mock)


@pytest.mark.asyncio
async def test_showcompetences_with_target_text_id_uses_target_user(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    target_user = _build_user_read_dto(db_id=40, telegram_id=400_001, first_name="Target")
    admin_user = _build_user_read_dto(db_id=41, telegram_id=400_002, first_name="Admin")
    service = StubUserService(
        users_by_tg={target_user.telegram_id: target_user},
        users_by_id={admin_user.id: admin_user, target_user.id: target_user},
        competencies_by_user_id={
            target_user.id: [CompetenceReadDTO(id=2, name="SQL", description=None)],
        },
    )
    message = _build_message(text="/showcompetences 400001", from_user_id=admin_user.telegram_id)

    reply_mock = AsyncMock()
    monkeypatch.setattr(Message, "reply", reply_mock)

    await handle_show_competences(message=message, user_service=service, user_id=admin_user.id)

    assert service.show_calls == [target_user.id]
    reply_text = _last_reply_text(reply_mock)
    assert "Target" in reply_text
    assert "SQL" in reply_text


@pytest.mark.asyncio
async def test_addcompetence_unknown_names_returns_validation_error(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    target_user = _build_user_read_dto(db_id=50, telegram_id=500_001, first_name="Target")
    service = StubUserService(
        users_by_tg={target_user.telegram_id: target_user},
        users_by_id={target_user.id: target_user},
        add_error=ValueError("Competence names not found: ['Unknown']"),
    )
    message = _build_message(text="/addcompetence 500001 Unknown", from_user_id=500_002)

    reply_mock = AsyncMock()
    monkeypatch.setattr(Message, "reply", reply_mock)

    await handle_add_competence(message=message, user_service=service)

    assert service.add_calls == [(target_user.id, ["Unknown"])]
    assert "Competence names not found" in _last_reply_text(reply_mock)


@pytest.mark.asyncio
async def test_addcompetence_distinguishes_missing_target_from_not_found_target(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    service = StubUserService(users_by_tg={}, users_by_id={})
    missing_target_message = _build_message(text="/addcompetence Python,SQL", from_user_id=600_001)
    not_found_target_message = _build_message(text="/addcompetence 999999 Python,SQL", from_user_id=600_001)
    reply_mock = AsyncMock()
    monkeypatch.setattr(Message, "reply", reply_mock)

    await handle_add_competence(message=missing_target_message, user_service=service)
    first_reply = _last_reply_text(reply_mock)
    assert "/addcompetence" in first_reply

    await handle_add_competence(message=not_found_target_message, user_service=service)
    second_reply = _last_reply_text(reply_mock)
    assert "not found" in second_reply.lower() or "не найден" in second_reply.lower()


@pytest.mark.asyncio
async def test_showcompetences_does_not_fallback_on_invalid_explicit_target(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    current_user = _build_user_read_dto(db_id=70, telegram_id=700_701, first_name="Admin")
    service = StubUserService(
        users_by_id={current_user.id: current_user},
        competencies_by_user_id={
            current_user.id: [CompetenceReadDTO(id=1, name="Python", description=None)],
        },
    )
    message = _build_message(text="/showcompetences 999999", from_user_id=current_user.telegram_id)
    reply_mock = AsyncMock()
    monkeypatch.setattr(Message, "reply", reply_mock)

    await handle_show_competences(message=message, user_service=service, user_id=current_user.id)

    assert service.show_calls == []
    assert "Python" not in _last_reply_text(reply_mock)
