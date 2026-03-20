from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from unittest.mock import AsyncMock

import pytest
from aiogram.types import Chat, Contact, Message, ReplyKeyboardRemove, User

from pybot.bot.dialogs.user_reg.handlers import _handle_contact_input
from pybot.bot.texts import (
    REGISTRATION_CONTACT_ACCEPTED,
    REGISTRATION_CONTACT_EMPTY,
    registration_existing_profile,
)
from pybot.core.constants import LevelTypeEnum
from pybot.dto import UserReadDTO
from pybot.dto.value_objects import Points


def _build_message(
    *,
    from_user_id: int = 700_001,
    phone_number: str | None = None,
) -> Message:
    sender = User(id=from_user_id, is_bot=False, first_name="Tester")
    contact: Contact | None = None
    if phone_number is not None:
        contact = Contact(phone_number=phone_number, first_name="Tester", user_id=from_user_id)

    return Message(
        message_id=1,
        date=datetime.now(UTC),
        chat=Chat(id=from_user_id, type="private"),
        from_user=sender,
        contact=contact,
    )


@dataclass(slots=True)
class StubDialogManager:
    dialog_data: dict[str, str | int | None] = field(default_factory=dict)
    next: AsyncMock = field(default_factory=AsyncMock)
    done: AsyncMock = field(default_factory=AsyncMock)


@dataclass(slots=True)
class StubUserService:
    existing_user: UserReadDTO | None = None
    phone_queries: list[str] = field(default_factory=list)

    async def find_user_by_phone(self, phone: str) -> UserReadDTO | None:
        self.phone_queries.append(phone)
        return self.existing_user


def _build_user_read_dto(user_id: int, telegram_id: int) -> UserReadDTO:
    return UserReadDTO(
        id=user_id,
        first_name="Tester",
        last_name="User",
        patronymic=None,
        telegram_id=telegram_id,
        academic_points=Points(value=0, point_type=LevelTypeEnum.ACADEMIC),
        reputation_points=Points(value=0, point_type=LevelTypeEnum.REPUTATION),
        join_date=datetime.now(UTC).date(),
    )


@pytest.mark.asyncio
async def test_on_contact_input_removes_keyboard_and_moves_to_next_step(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    message = _build_message(phone_number="+79990001122")
    manager = StubDialogManager()
    user_service = StubUserService(existing_user=None)
    answer_mock = AsyncMock()
    monkeypatch.setattr(Message, "answer", answer_mock)

    await _handle_contact_input(
        message=message,
        manager=manager,  # type: ignore[arg-type]
        user_service=user_service,  # type: ignore[arg-type]
    )

    assert user_service.phone_queries == ["+79990001122"]
    assert manager.dialog_data["phone_number"] == "+79990001122"
    assert manager.dialog_data["tg_id"] == 700_001
    manager.next.assert_awaited_once()
    manager.done.assert_not_awaited()

    assert answer_mock.await_count == 1
    await_args = answer_mock.await_args
    assert await_args is not None
    assert await_args.args[0] == REGISTRATION_CONTACT_ACCEPTED
    assert isinstance(await_args.kwargs.get("reply_markup"), ReplyKeyboardRemove)


@pytest.mark.asyncio
async def test_on_contact_input_removes_keyboard_for_existing_user_and_finishes(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    message = _build_message(phone_number="+79990001123")
    manager = StubDialogManager()
    user_service = StubUserService(existing_user=_build_user_read_dto(user_id=42, telegram_id=700_001))
    answer_mock = AsyncMock()
    monkeypatch.setattr(Message, "answer", answer_mock)

    await _handle_contact_input(
        message=message,
        manager=manager,  # type: ignore[arg-type]
        user_service=user_service,  # type: ignore[arg-type]
    )

    assert user_service.phone_queries == ["+79990001123"]
    manager.done.assert_awaited_once()
    manager.next.assert_not_awaited()
    assert manager.dialog_data == {}

    assert answer_mock.await_count == 1
    await_args = answer_mock.await_args
    assert await_args is not None
    assert await_args.args[0] == registration_existing_profile(42)
    assert isinstance(await_args.kwargs.get("reply_markup"), ReplyKeyboardRemove)


@pytest.mark.asyncio
async def test_on_contact_input_with_empty_contact_keeps_keyboard_and_does_not_advance(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    message = _build_message(phone_number=None)
    manager = StubDialogManager()
    user_service = StubUserService(existing_user=None)
    answer_mock = AsyncMock()
    monkeypatch.setattr(Message, "answer", answer_mock)

    await _handle_contact_input(
        message=message,
        manager=manager,  # type: ignore[arg-type]
        user_service=user_service,  # type: ignore[arg-type]
    )

    assert user_service.phone_queries == []
    manager.next.assert_not_awaited()
    manager.done.assert_not_awaited()
    assert manager.dialog_data == {}

    assert answer_mock.await_count == 1
    await_args = answer_mock.await_args
    assert await_args is not None
    assert await_args.args[0] == REGISTRATION_CONTACT_EMPTY
    assert "reply_markup" not in await_args.kwargs
