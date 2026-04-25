from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime

import pytest

from pybot.core.constants import PointsTypeEnum
from pybot.dto import NotifyDTO, WeeklyLeaderboardRowDTO
from pybot.services.leaderboard import LeaderboardService
from pybot.services.ports import NotificationPort
from pybot.services.weekly_leaderboard_publisher import WeeklyLeaderboardPublisherService


@dataclass(slots=True)
class LeaderboardServiceStub(LeaderboardService):
    responses: dict[PointsTypeEnum, list[WeeklyLeaderboardRowDTO]] = field(default_factory=dict)
    calls: list[tuple[PointsTypeEnum, int, str]] = field(default_factory=list)

    async def get_previous_calendar_week_leaderboard(
        self,
        *,
        points_type: PointsTypeEnum,
        limit: int = 10,
        business_tz: str = "Asia/Yekaterinburg",
    ) -> list[WeeklyLeaderboardRowDTO]:
        self.calls.append((points_type, limit, business_tz))
        return self.responses.get(points_type, [])


class NotificationPortSpy(NotificationPort):
    def __init__(self) -> None:
        self.messages: list[NotifyDTO] = []

    async def send_role_request_to_admin(self, request_id: int, requester_user_id: int, role_name: str) -> None:
        return None

    async def send_message(self, message_data: NotifyDTO) -> None:
        self.messages.append(message_data)


def _row(
    *,
    user_id: int,
    telegram_id: int,
    first_name: str,
    points_type: PointsTypeEnum,
    total_points_delta: int,
) -> WeeklyLeaderboardRowDTO:
    return WeeklyLeaderboardRowDTO(
        user_id=user_id,
        telegram_id=telegram_id,
        first_name=first_name,
        last_name="Test",
        patronymic=None,
        total_points_delta=total_points_delta,
        points_type=points_type,
        period_start=datetime(2026, 4, 6, 0, 0, 0, tzinfo=UTC),
        period_end=datetime(2026, 4, 13, 0, 0, 0, tzinfo=UTC),
    )


@pytest.mark.asyncio
async def test_weekly_leaderboard_publisher_service_sends_rendered_html_message() -> None:
    leaderboard_stub = LeaderboardServiceStub(
        responses={
            PointsTypeEnum.ACADEMIC: [
                _row(
                    user_id=1,
                    telegram_id=700_001,
                    first_name="Ivan",
                    points_type=PointsTypeEnum.ACADEMIC,
                    total_points_delta=42,
                )
            ],
            PointsTypeEnum.REPUTATION: [
                _row(
                    user_id=2,
                    telegram_id=700_002,
                    first_name="Petr",
                    points_type=PointsTypeEnum.REPUTATION,
                    total_points_delta=9,
                )
            ],
        }
    )
    notification_port = NotificationPortSpy()
    service = WeeklyLeaderboardPublisherService(
        leaderboard_service=leaderboard_stub,
        notification_port=notification_port,
    )

    await service.publish_weekly(
        recipient_id=-100_987_654_321,
        limit=5,
        business_tz="Asia/Yekaterinburg",
    )

    assert leaderboard_stub.calls == [
        (PointsTypeEnum.ACADEMIC, 5, "Asia/Yekaterinburg"),
        (PointsTypeEnum.REPUTATION, 5, "Asia/Yekaterinburg"),
    ]
    assert len(notification_port.messages) == 1
    payload = notification_port.messages[0]
    assert payload.recipient_id == -100_987_654_321
    assert payload.parse_mode == "HTML"
    assert "<b>Академические баллы</b>" in payload.message
    assert "<b>Репутационные баллы</b>" in payload.message
