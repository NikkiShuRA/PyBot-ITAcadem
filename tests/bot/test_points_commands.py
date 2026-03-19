from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, date, datetime
from typing import cast
from unittest.mock import AsyncMock

import pytest
from aiogram.types import Chat, Message, User

from pybot.bot.handlers.points import grand_points
from pybot.bot.handlers.points.grand_points import _extract_points_and_reason, _handle_points_command
from pybot.bot.texts import POINTS_REASON_QUOTES_REQUIRED
from pybot.core.constants import LevelTypeEnum, TaskScheduleKind
from pybot.dto import UserReadDTO
from pybot.dto.value_objects import Points
from pybot.services.notification_facade import NotificationFacade
from pybot.services.points import PointsService
from pybot.services.users import UserService


def _build_message(*, text: str, from_user_id: int = 720_001) -> Message:
    sender = User(id=from_user_id, is_bot=False, first_name="Admin")
    return Message(
        message_id=1,
        date=datetime.now(UTC),
        chat=Chat(id=from_user_id, type="private"),
        from_user=sender,
        text=text,
    )


def _build_user_read_dto(*, db_id: int, telegram_id: int, first_name: str) -> UserReadDTO:
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


@dataclass(slots=True)
class StubUserService:
    users_by_tg: dict[int, UserReadDTO] = field(default_factory=dict)
    telegram_queries: list[int] = field(default_factory=list)

    async def find_user_by_telegram_id(self, tg_id: int) -> UserReadDTO | None:
        self.telegram_queries.append(tg_id)
        return self.users_by_tg.get(tg_id)


@dataclass(slots=True)
class StubPointsService:
    change_points: AsyncMock = field(default_factory=AsyncMock)


@dataclass(slots=True)
class StubNotificationFacade:
    notify_user: AsyncMock = field(default_factory=AsyncMock)


def _last_reply_text(reply_mock: AsyncMock) -> str:
    assert reply_mock.await_args_list
    return str(reply_mock.await_args_list[-1].args[0])


@pytest.mark.asyncio
async def test_extract_points_and_reason_parses_positive_points_with_reason(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    message = _build_message(text='/academic_points 25 "Great progress"')
    reply_mock = AsyncMock()
    monkeypatch.setattr(Message, "reply", reply_mock)

    points, reason = await _extract_points_and_reason(message)

    assert points == 25
    assert reason == "Great progress"
    reply_mock.assert_not_awaited()


@pytest.mark.asyncio
async def test_extract_points_and_reason_parses_negative_points(monkeypatch: pytest.MonkeyPatch) -> None:
    message = _build_message(text="/reputation_points -7 'Too noisy in chat'")
    reply_mock = AsyncMock()
    monkeypatch.setattr(Message, "reply", reply_mock)

    points, reason = await _extract_points_and_reason(message)

    assert points == -7
    assert reason == "Too noisy in chat"
    reply_mock.assert_not_awaited()


@pytest.mark.asyncio
async def test_extract_points_and_reason_rejects_unquoted_reason(monkeypatch: pytest.MonkeyPatch) -> None:
    message = _build_message(text="/academic_points 10 because this was helpful")
    reply_mock = AsyncMock()
    monkeypatch.setattr(Message, "reply", reply_mock)

    points, reason = await _extract_points_and_reason(message)

    assert points is None
    assert reason is None
    reply_mock.assert_awaited_once_with(POINTS_REASON_QUOTES_REQUIRED)


@pytest.mark.asyncio
async def test_handle_points_command_changes_points_and_enqueues_notification(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    recipient = _build_user_read_dto(db_id=10, telegram_id=720_002, first_name="Student")
    giver = _build_user_read_dto(db_id=11, telegram_id=720_001, first_name="Admin")
    user_service = StubUserService(users_by_tg={recipient.telegram_id: recipient, giver.telegram_id: giver})
    points_service = StubPointsService()
    notification_facade = StubNotificationFacade()
    message = _build_message(text='/academic_points 15 "Great progress"', from_user_id=giver.telegram_id)
    reply_mock = AsyncMock()
    monkeypatch.setattr(Message, "reply", reply_mock)
    monkeypatch.setattr(grand_points, "_get_target_user_id_from_reply", AsyncMock(return_value=None))
    monkeypatch.setattr(grand_points, "_get_target_user_id_from_mention", AsyncMock(return_value=None))
    monkeypatch.setattr(grand_points, "_get_target_user_id_from_text", AsyncMock(return_value=recipient.telegram_id))

    await _handle_points_command(
        message=message,
        points_type=LevelTypeEnum.ACADEMIC,
        points_service=cast(PointsService, points_service),
        user_service=cast(UserService, user_service),
        notification_facade=cast(NotificationFacade, notification_facade),
    )

    points_service.change_points.assert_awaited_once()
    sent_adjustment = points_service.change_points.await_args.args[0]
    assert sent_adjustment.recipient_id == recipient.id
    assert sent_adjustment.giver_id == giver.id
    assert sent_adjustment.points.value == 15
    assert sent_adjustment.reason == "Great progress"

    notification_facade.notify_user.assert_awaited_once()
    notify_dto = notification_facade.notify_user.await_args.args[0]
    assert notify_dto.user_id == recipient.telegram_id
    assert notify_dto.kind is TaskScheduleKind.IMMEDIATE
    assert giver.first_name in notify_dto.message
    assert "академических" in notify_dto.message
    assert "Great progress" in notify_dto.message

    reply_mock.assert_awaited_once()
    reply_text = _last_reply_text(reply_mock)
    assert str(recipient.telegram_id) in reply_text
    assert "Great progress" in reply_text


@pytest.mark.asyncio
async def test_handle_points_command_stops_when_recipient_or_giver_is_missing(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    recipient = _build_user_read_dto(db_id=20, telegram_id=720_003, first_name="Student")
    user_service = StubUserService(users_by_tg={recipient.telegram_id: recipient})
    points_service = StubPointsService()
    notification_facade = StubNotificationFacade()
    message = _build_message(text='/academic_points 12 "Helpful review"', from_user_id=720_999)
    reply_mock = AsyncMock()
    monkeypatch.setattr(Message, "reply", reply_mock)
    monkeypatch.setattr(grand_points, "_get_target_user_id_from_reply", AsyncMock(return_value=None))
    monkeypatch.setattr(grand_points, "_get_target_user_id_from_mention", AsyncMock(return_value=None))
    monkeypatch.setattr(grand_points, "_get_target_user_id_from_text", AsyncMock(return_value=recipient.telegram_id))

    await _handle_points_command(
        message=message,
        points_type=LevelTypeEnum.ACADEMIC,
        points_service=cast(PointsService, points_service),
        user_service=cast(UserService, user_service),
        notification_facade=cast(NotificationFacade, notification_facade),
    )

    points_service.change_points.assert_not_awaited()
    notification_facade.notify_user.assert_not_awaited()
    reply_mock.assert_not_awaited()


@pytest.mark.asyncio
async def test_handle_points_command_reports_points_service_failure(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    recipient = _build_user_read_dto(db_id=30, telegram_id=720_004, first_name="Student")
    giver = _build_user_read_dto(db_id=31, telegram_id=720_001, first_name="Admin")
    user_service = StubUserService(users_by_tg={recipient.telegram_id: recipient, giver.telegram_id: giver})
    points_service = StubPointsService(change_points=AsyncMock(side_effect=RuntimeError("boom")))
    notification_facade = StubNotificationFacade()
    message = _build_message(text='/academic_points 5 "For helping"', from_user_id=giver.telegram_id)
    reply_mock = AsyncMock()
    monkeypatch.setattr(Message, "reply", reply_mock)
    monkeypatch.setattr(grand_points, "_get_target_user_id_from_reply", AsyncMock(return_value=None))
    monkeypatch.setattr(grand_points, "_get_target_user_id_from_mention", AsyncMock(return_value=None))
    monkeypatch.setattr(grand_points, "_get_target_user_id_from_text", AsyncMock(return_value=recipient.telegram_id))

    await _handle_points_command(
        message=message,
        points_type=LevelTypeEnum.ACADEMIC,
        points_service=cast(PointsService, points_service),
        user_service=cast(UserService, user_service),
        notification_facade=cast(NotificationFacade, notification_facade),
    )

    points_service.change_points.assert_awaited_once()
    notification_facade.notify_user.assert_not_awaited()
    reply_mock.assert_awaited_once()
    assert "Не удалось изменить баллы" in _last_reply_text(reply_mock)
