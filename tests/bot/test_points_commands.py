from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, date, datetime
from typing import cast
from unittest.mock import AsyncMock, Mock

import pytest
from aiogram.types import Chat, Message, User

from pybot.presentation.bot import grand_points_handlers as grand_points
from pybot.presentation.texts import (
    POINTS_AMOUNT_REQUIRED,
    POINTS_COMMAND_INVALID_FORMAT,
    POINTS_OPERATION_FAILED,
    POINTS_REASON_QUOTES_REQUIRED,
    POINTS_UNEXPECTED_ERROR,
    TARGET_NOT_FOUND,
    points_invalid_value,
)
from pybot.core.constants import PointsTypeEnum, TaskScheduleKind
from pybot.domain.exceptions import DomainError, InvalidPointsValueError, UserNotFoundError, ZeroPointsAdjustmentError
from pybot.dto import UserReadDTO
from pybot.dto.value_objects import Points
from pybot.services.notification_facade import NotificationFacade
from pybot.services.points import PointsService
from pybot.services.user_services import UserService


def _build_message(*, text: str | None, from_user_id: int | None = 720_001) -> Message:
    sender = None
    if from_user_id is not None:
        sender = User(id=from_user_id, is_bot=False, first_name="Admin")

    return Message(
        message_id=1,
        date=datetime.now(UTC),
        chat=Chat(id=from_user_id or 0, type="private"),
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
        academic_points=Points(value=0, point_type=PointsTypeEnum.ACADEMIC),
        reputation_points=Points(value=0, point_type=PointsTypeEnum.REPUTATION),
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


def _patch_logger_methods(monkeypatch: pytest.MonkeyPatch) -> dict[str, Mock]:
    mocks = {
        "warning": Mock(),
        "error": Mock(),
        "exception": Mock(),
    }
    for method_name, mock in mocks.items():
        monkeypatch.setattr(grand_points.logger, method_name, mock)
    return mocks


@pytest.mark.asyncio
async def test_extract_points_and_reason_parses_positive_points_with_reason(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    message = _build_message(text='/academic_points 25 "Great progress"')
    reply_mock = AsyncMock()
    monkeypatch.setattr(Message, "reply", reply_mock)

    points, reason = await grand_points._extract_points_and_reason(message)

    assert points == 25
    assert reason == "Great progress"
    reply_mock.assert_not_awaited()


@pytest.mark.asyncio
async def test_extract_points_and_reason_parses_negative_points(monkeypatch: pytest.MonkeyPatch) -> None:
    message = _build_message(text="/reputation_points -7 'Too noisy in chat'")
    reply_mock = AsyncMock()
    monkeypatch.setattr(Message, "reply", reply_mock)

    points, reason = await grand_points._extract_points_and_reason(message)

    assert points == -7
    assert reason == "Too noisy in chat"
    reply_mock.assert_not_awaited()


@pytest.mark.asyncio
async def test_extract_points_and_reason_when_text_is_invalid_replies_invalid_format(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    message = _build_message(text=None)
    reply_mock = AsyncMock()
    monkeypatch.setattr(Message, "reply", reply_mock)

    points, reason = await grand_points._extract_points_and_reason(message)

    assert points is None
    assert reason is None
    reply_mock.assert_awaited_once_with(POINTS_COMMAND_INVALID_FORMAT)


@pytest.mark.asyncio
async def test_extract_points_and_reason_when_number_missing_replies_points_amount_required(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    message = _build_message(text='/academic_points "Great progress"')
    reply_mock = AsyncMock()
    monkeypatch.setattr(Message, "reply", reply_mock)

    points, reason = await grand_points._extract_points_and_reason(message)

    assert points is None
    assert reason is None
    reply_mock.assert_awaited_once_with(POINTS_AMOUNT_REQUIRED)


@pytest.mark.asyncio
async def test_extract_points_and_reason_rejects_unquoted_reason(monkeypatch: pytest.MonkeyPatch) -> None:
    message = _build_message(text="/academic_points 10 because this was helpful")
    reply_mock = AsyncMock()
    monkeypatch.setattr(Message, "reply", reply_mock)

    points, reason = await grand_points._extract_points_and_reason(message)

    assert points is None
    assert reason is None
    reply_mock.assert_awaited_once_with(POINTS_REASON_QUOTES_REQUIRED)


@pytest.mark.asyncio
async def test_prepare_points_command_context_when_message_has_no_from_user_returns_none(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    user_service = StubUserService()
    message = _build_message(text='/academic_points 12 "Helpful review"', from_user_id=None)
    reply_mock = AsyncMock()
    monkeypatch.setattr(Message, "reply", reply_mock)

    context = await grand_points._prepare_points_command_context(
        message,
        PointsTypeEnum.ACADEMIC,
        cast(UserService, user_service),
    )

    assert context is None
    assert user_service.telegram_queries == []
    reply_mock.assert_not_awaited()


@pytest.mark.asyncio
async def test_prepare_points_command_context_when_target_not_resolved_logs_warning_and_returns_none(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    user_service = StubUserService()
    message = _build_message(text='/academic_points 12 "Helpful review"')
    reply_mock = AsyncMock()
    logger_mocks = _patch_logger_methods(monkeypatch)
    monkeypatch.setattr(Message, "reply", reply_mock)
    monkeypatch.setattr(grand_points, "_get_target_user_id_from_reply", AsyncMock(return_value=None))
    monkeypatch.setattr(grand_points, "_get_target_user_id_from_mention", AsyncMock(return_value=None))
    monkeypatch.setattr(grand_points, "_get_target_user_id_from_text", AsyncMock(return_value=None))

    context = await grand_points._prepare_points_command_context(
        message,
        PointsTypeEnum.ACADEMIC,
        cast(UserService, user_service),
    )

    assert context is None
    logger_mocks["warning"].assert_called_once()
    assert user_service.telegram_queries == []
    reply_mock.assert_not_awaited()


@pytest.mark.asyncio
async def test_prepare_points_command_context_when_points_value_invalid_replies_with_invalid_value(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    user_service = StubUserService()
    too_large_points = 2**31
    message = _build_message(text=f'/academic_points {too_large_points} "Helpful review"')
    reply_mock = AsyncMock()
    monkeypatch.setattr(Message, "reply", reply_mock)
    monkeypatch.setattr(grand_points, "_get_target_user_id_from_reply", AsyncMock(return_value=None))
    monkeypatch.setattr(grand_points, "_get_target_user_id_from_mention", AsyncMock(return_value=None))
    monkeypatch.setattr(grand_points, "_get_target_user_id_from_text", AsyncMock(return_value=720_099))

    context = await grand_points._prepare_points_command_context(
        message,
        PointsTypeEnum.ACADEMIC,
        cast(UserService, user_service),
    )

    assert context is None
    reply_mock.assert_awaited_once_with(points_invalid_value(too_large_points))
    assert user_service.telegram_queries == []


@pytest.mark.asyncio
async def test_prepare_points_command_context_when_recipient_or_giver_missing_logs_warning_and_returns_none(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    recipient = _build_user_read_dto(db_id=20, telegram_id=720_003, first_name="Student")
    user_service = StubUserService(users_by_tg={recipient.telegram_id: recipient})
    message = _build_message(text='/academic_points 12 "Helpful review"', from_user_id=720_999)
    reply_mock = AsyncMock()
    logger_mocks = _patch_logger_methods(monkeypatch)
    monkeypatch.setattr(Message, "reply", reply_mock)
    monkeypatch.setattr(grand_points, "_get_target_user_id_from_reply", AsyncMock(return_value=None))
    monkeypatch.setattr(grand_points, "_get_target_user_id_from_mention", AsyncMock(return_value=None))
    monkeypatch.setattr(grand_points, "_get_target_user_id_from_text", AsyncMock(return_value=recipient.telegram_id))

    context = await grand_points._prepare_points_command_context(
        message,
        PointsTypeEnum.ACADEMIC,
        cast(UserService, user_service),
    )

    assert context is None
    logger_mocks["warning"].assert_called_once_with("Failed to resolve giver or recipient for points command")
    reply_mock.assert_not_awaited()


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

    await grand_points._handle_points_command(
        message=message,
        points_type=PointsTypeEnum.ACADEMIC,
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
    assert notify_dto.recipient_id == recipient.telegram_id
    assert notify_dto.kind is TaskScheduleKind.IMMEDIATE
    assert giver.first_name in notify_dto.message
    assert "академ" in notify_dto.message.lower()
    assert "Great progress" in notify_dto.message

    reply_mock.assert_awaited_once()
    reply_text = _last_reply_text(reply_mock)
    assert recipient.first_name in reply_text
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

    await grand_points._handle_points_command(
        message=message,
        points_type=PointsTypeEnum.ACADEMIC,
        points_service=cast(PointsService, points_service),
        user_service=cast(UserService, user_service),
        notification_facade=cast(NotificationFacade, notification_facade),
    )

    points_service.change_points.assert_not_awaited()
    notification_facade.notify_user.assert_not_awaited()
    reply_mock.assert_not_awaited()


@pytest.mark.asyncio
async def test_handle_points_command_when_notification_fails_still_replies_success(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    recipient = _build_user_read_dto(db_id=12, telegram_id=720_012, first_name="Student")
    giver = _build_user_read_dto(db_id=13, telegram_id=720_001, first_name="Admin")
    user_service = StubUserService(users_by_tg={recipient.telegram_id: recipient, giver.telegram_id: giver})
    points_service = StubPointsService()
    notification_facade = StubNotificationFacade(notify_user=AsyncMock(side_effect=RuntimeError("queue down")))
    message = _build_message(text='/academic_points 9 "For review"', from_user_id=giver.telegram_id)
    reply_mock = AsyncMock()
    logger_mocks = _patch_logger_methods(monkeypatch)
    monkeypatch.setattr(Message, "reply", reply_mock)
    monkeypatch.setattr(grand_points, "_get_target_user_id_from_reply", AsyncMock(return_value=None))
    monkeypatch.setattr(grand_points, "_get_target_user_id_from_mention", AsyncMock(return_value=None))
    monkeypatch.setattr(grand_points, "_get_target_user_id_from_text", AsyncMock(return_value=recipient.telegram_id))

    await grand_points._handle_points_command(
        message=message,
        points_type=PointsTypeEnum.ACADEMIC,
        points_service=cast(PointsService, points_service),
        user_service=cast(UserService, user_service),
        notification_facade=cast(NotificationFacade, notification_facade),
    )

    points_service.change_points.assert_awaited_once()
    notification_facade.notify_user.assert_awaited_once()
    logger_mocks["exception"].assert_called_once()
    reply_mock.assert_awaited_once()
    assert recipient.first_name in _last_reply_text(reply_mock)


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

    await grand_points._handle_points_command(
        message=message,
        points_type=PointsTypeEnum.ACADEMIC,
        points_service=cast(PointsService, points_service),
        user_service=cast(UserService, user_service),
        notification_facade=cast(NotificationFacade, notification_facade),
    )

    points_service.change_points.assert_awaited_once()
    notification_facade.notify_user.assert_not_awaited()
    reply_mock.assert_awaited_once()
    assert POINTS_OPERATION_FAILED in _last_reply_text(reply_mock)


@pytest.mark.asyncio
async def test_handle_academic_points_when_user_not_found_replies_target_not_found(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    message = _build_message(text="/academic_points")
    reply_mock = AsyncMock()
    logger_mocks = _patch_logger_methods(monkeypatch)
    monkeypatch.setattr(Message, "reply", reply_mock)
    monkeypatch.setattr(
        grand_points,
        "_handle_points_command",
        AsyncMock(side_effect=UserNotFoundError(telegram_id=999_999)),
    )

    await grand_points.handle_academic_points(
        message=message,
        user_service=StubUserService(),
        points_service=StubPointsService(),
        notification_facade=StubNotificationFacade(),
    )

    reply_mock.assert_awaited_once_with(TARGET_NOT_FOUND)
    logger_mocks["warning"].assert_called_once_with("User not found in academic points command")


@pytest.mark.asyncio
async def test_handle_academic_points_when_zero_adjustment_replies_invalid_zero_value(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    message = _build_message(text="/academic_points")
    reply_mock = AsyncMock()
    monkeypatch.setattr(Message, "reply", reply_mock)
    monkeypatch.setattr(grand_points, "_handle_points_command", AsyncMock(side_effect=ZeroPointsAdjustmentError()))

    await grand_points.handle_academic_points(
        message=message,
        user_service=StubUserService(),
        points_service=StubPointsService(),
        notification_facade=StubNotificationFacade(),
    )

    reply_mock.assert_awaited_once_with(points_invalid_value(0))


@pytest.mark.asyncio
async def test_handle_academic_points_when_invalid_points_value_replies_invalid_value_from_error(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    message = _build_message(text="/academic_points")
    reply_mock = AsyncMock()
    logger_mocks = _patch_logger_methods(monkeypatch)
    monkeypatch.setattr(Message, "reply", reply_mock)
    monkeypatch.setattr(
        grand_points,
        "_handle_points_command",
        AsyncMock(side_effect=InvalidPointsValueError(42)),
    )

    await grand_points.handle_academic_points(
        message=message,
        user_service=StubUserService(),
        points_service=StubPointsService(),
        notification_facade=StubNotificationFacade(),
    )

    reply_mock.assert_awaited_once_with(points_invalid_value(42))
    logger_mocks["exception"].assert_called_once_with("Invalid points")


@pytest.mark.asyncio
async def test_handle_academic_points_when_domain_error_replies_operation_failed(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    message = _build_message(text="/academic_points")
    reply_mock = AsyncMock()
    logger_mocks = _patch_logger_methods(monkeypatch)
    monkeypatch.setattr(Message, "reply", reply_mock)
    monkeypatch.setattr(
        grand_points,
        "_handle_points_command",
        AsyncMock(side_effect=DomainError("domain failure")),
    )

    await grand_points.handle_academic_points(
        message=message,
        user_service=StubUserService(),
        points_service=StubPointsService(),
        notification_facade=StubNotificationFacade(),
    )

    reply_mock.assert_awaited_once_with(POINTS_OPERATION_FAILED)
    logger_mocks["error"].assert_called_once_with("Domain error in academic points command", exc_info=True)


@pytest.mark.asyncio
async def test_handle_academic_points_when_unexpected_error_replies_unexpected_error(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    message = _build_message(text="/academic_points")
    reply_mock = AsyncMock()
    logger_mocks = _patch_logger_methods(monkeypatch)
    monkeypatch.setattr(Message, "reply", reply_mock)
    monkeypatch.setattr(
        grand_points,
        "_handle_points_command",
        AsyncMock(side_effect=RuntimeError("boom")),
    )

    await grand_points.handle_academic_points(
        message=message,
        user_service=StubUserService(),
        points_service=StubPointsService(),
        notification_facade=StubNotificationFacade(),
    )

    reply_mock.assert_awaited_once_with(POINTS_UNEXPECTED_ERROR)
    logger_mocks["exception"].assert_called_once_with("Unexpected error in handle_academic_points")


@pytest.mark.asyncio
async def test_handle_reputation_points_when_user_not_found_replies_target_not_found(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    message = _build_message(text="/reputation_points")
    reply_mock = AsyncMock()
    logger_mocks = _patch_logger_methods(monkeypatch)
    monkeypatch.setattr(Message, "reply", reply_mock)
    monkeypatch.setattr(
        grand_points,
        "_handle_points_command",
        AsyncMock(side_effect=UserNotFoundError(telegram_id=999_999)),
    )

    await grand_points.handle_reputation_points(
        message=message,
        user_service=StubUserService(),
        points_service=StubPointsService(),
        notification_facade=StubNotificationFacade(),
    )

    reply_mock.assert_awaited_once_with(TARGET_NOT_FOUND)
    logger_mocks["warning"].assert_called_once_with("User not found in reputation points command")


@pytest.mark.asyncio
async def test_handle_reputation_points_when_zero_adjustment_replies_invalid_zero_value(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    message = _build_message(text="/reputation_points")
    reply_mock = AsyncMock()
    monkeypatch.setattr(Message, "reply", reply_mock)
    monkeypatch.setattr(grand_points, "_handle_points_command", AsyncMock(side_effect=ZeroPointsAdjustmentError()))

    await grand_points.handle_reputation_points(
        message=message,
        user_service=StubUserService(),
        points_service=StubPointsService(),
        notification_facade=StubNotificationFacade(),
    )

    reply_mock.assert_awaited_once_with(points_invalid_value(0))


@pytest.mark.asyncio
async def test_handle_reputation_points_when_invalid_points_value_replies_invalid_value_from_error(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    message = _build_message(text="/reputation_points")
    reply_mock = AsyncMock()
    logger_mocks = _patch_logger_methods(monkeypatch)
    monkeypatch.setattr(Message, "reply", reply_mock)
    monkeypatch.setattr(
        grand_points,
        "_handle_points_command",
        AsyncMock(side_effect=InvalidPointsValueError(77)),
    )

    await grand_points.handle_reputation_points(
        message=message,
        user_service=StubUserService(),
        points_service=StubPointsService(),
        notification_facade=StubNotificationFacade(),
    )

    reply_mock.assert_awaited_once_with(points_invalid_value(77))
    logger_mocks["exception"].assert_called_once_with("Invalid points")


@pytest.mark.asyncio
async def test_handle_reputation_points_when_domain_error_replies_operation_failed(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    message = _build_message(text="/reputation_points")
    reply_mock = AsyncMock()
    logger_mocks = _patch_logger_methods(monkeypatch)
    monkeypatch.setattr(Message, "reply", reply_mock)
    monkeypatch.setattr(
        grand_points,
        "_handle_points_command",
        AsyncMock(side_effect=DomainError("domain failure")),
    )

    await grand_points.handle_reputation_points(
        message=message,
        user_service=StubUserService(),
        points_service=StubPointsService(),
        notification_facade=StubNotificationFacade(),
    )

    reply_mock.assert_awaited_once_with(POINTS_OPERATION_FAILED)
    logger_mocks["exception"].assert_called_once_with("Domain error in handle_reputation_points")


@pytest.mark.asyncio
async def test_handle_reputation_points_when_unexpected_error_replies_unexpected_error(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    message = _build_message(text="/reputation_points")
    reply_mock = AsyncMock()
    logger_mocks = _patch_logger_methods(monkeypatch)
    monkeypatch.setattr(Message, "reply", reply_mock)
    monkeypatch.setattr(
        grand_points,
        "_handle_points_command",
        AsyncMock(side_effect=RuntimeError("boom")),
    )

    await grand_points.handle_reputation_points(
        message=message,
        user_service=StubUserService(),
        points_service=StubPointsService(),
        notification_facade=StubNotificationFacade(),
    )

    reply_mock.assert_awaited_once_with(POINTS_UNEXPECTED_ERROR)
    logger_mocks["exception"].assert_called_once_with("Unexpected error in handle_reputation_points")
