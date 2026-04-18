from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import cast
from unittest.mock import AsyncMock

import pytest
from aiogram.types import Chat, Message, User

from pybot.bot.handlers.points.leaderboard import handle_leaderboard
from pybot.bot.texts import LEADERBOARD_UNEXPECTED_ERROR
from pybot.core.constants import PointsTypeEnum
from pybot.dto import WeeklyLeaderboardRowDTO
from pybot.dto.leaderboard_dto import LeaderboardPeriod
from pybot.services import LeaderboardService


def _build_message(*, text: str, from_user_id: int = 730_001) -> Message:
    sender = User(id=from_user_id, is_bot=False, first_name="Viewer")
    return Message(
        message_id=1,
        date=datetime.now(UTC),
        chat=Chat(id=from_user_id, type="private"),
        from_user=sender,
        text=text,
    )


def _build_row(
    *,
    user_id: int,
    telegram_id: int,
    first_name: str,
    last_name: str,
    total_points_delta: int,
    points_type: PointsTypeEnum,
) -> WeeklyLeaderboardRowDTO:
    return WeeklyLeaderboardRowDTO(
        user_id=user_id,
        telegram_id=telegram_id,
        first_name=first_name,
        last_name=last_name,
        patronymic=None,
        total_points_delta=total_points_delta,
        points_type=points_type,
        period_start=datetime(2026, 3, 24, 0, 0, 0, tzinfo=UTC),
        period_end=datetime(2026, 3, 31, 0, 0, 0, tzinfo=UTC),
    )


@dataclass(slots=True)
class StubLeaderboardService:
    responses_by_type: dict[PointsTypeEnum, list[WeeklyLeaderboardRowDTO]] = field(default_factory=dict)
    calls: list[PointsTypeEnum] = field(default_factory=list)
    should_raise: bool = False

    def get_previous_calendar_week_period(
        self,
        *,
        business_tz: str = "Asia/Yekaterinburg",
    ) -> LeaderboardPeriod:
        del business_tz
        return LeaderboardPeriod(
            start=datetime(2026, 3, 24, 0, 0, 0, tzinfo=UTC),
            end=datetime(2026, 3, 31, 0, 0, 0, tzinfo=UTC),
        )

    async def get_previous_calendar_week_leaderboard(
        self,
        *,
        points_type: PointsTypeEnum,
        limit: int = 10,
        business_tz: str = "Asia/Yekaterinburg",
    ) -> list[WeeklyLeaderboardRowDTO]:
        del limit
        del business_tz
        self.calls.append(points_type)
        if self.should_raise:
            raise RuntimeError("boom")
        return self.responses_by_type.get(points_type, [])


@pytest.mark.asyncio
async def test_handle_leaderboard_renders_both_sections_as_html(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    leaderboard_service = StubLeaderboardService(
        responses_by_type={
            PointsTypeEnum.ACADEMIC: [
                _build_row(
                    user_id=1,
                    telegram_id=101,
                    first_name="Иван",
                    last_name="Петров",
                    total_points_delta=42,
                    points_type=PointsTypeEnum.ACADEMIC,
                )
            ],
            PointsTypeEnum.REPUTATION: [],
        }
    )
    message = _build_message(text="/leaderboard")
    answer_mock = AsyncMock()
    monkeypatch.setattr(Message, "answer", answer_mock)

    await handle_leaderboard(
        message=message,
        leaderboard_service=cast(LeaderboardService, leaderboard_service),
    )

    assert leaderboard_service.calls == [PointsTypeEnum.ACADEMIC, PointsTypeEnum.REPUTATION]
    answer_mock.assert_awaited_once()
    await_args = answer_mock.await_args
    assert await_args is not None
    assert await_args.kwargs["parse_mode"] == "HTML"
    response_text = str(await_args.args[0])
    assert "24.03.2026 - 30.03.2026" in response_text
    assert "<b>Академические баллы</b>" in response_text
    assert "<b>Репутационные баллы</b>" in response_text
    assert "Иван Петров" in response_text


@pytest.mark.asyncio
async def test_handle_leaderboard_returns_safe_fallback_on_error(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    leaderboard_service = StubLeaderboardService(should_raise=True)
    message = _build_message(text="/leaderboard")
    answer_mock = AsyncMock()
    monkeypatch.setattr(Message, "answer", answer_mock)

    await handle_leaderboard(
        message=message,
        leaderboard_service=cast(LeaderboardService, leaderboard_service),
    )

    answer_mock.assert_awaited_once_with(LEADERBOARD_UNEXPECTED_ERROR)
