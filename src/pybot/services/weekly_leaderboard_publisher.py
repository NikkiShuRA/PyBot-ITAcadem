from __future__ import annotations

from ..core.constants import PointsTypeEnum
from ..dto import NotifyDTO
from ..presentation.texts import render_leaderboard_message
from .leaderboard import LeaderboardService
from .ports import NotificationPort


class WeeklyLeaderboardPublisherService:
    """Orchestrate weekly leaderboard publication to one transport recipient."""

    def __init__(
        self,
        leaderboard_service: LeaderboardService,
        notification_port: NotificationPort,
    ) -> None:
        self._leaderboard_service = leaderboard_service
        self._notification_port = notification_port

    async def publish_weekly(
        self,
        *,
        recipient_id: int,
        limit: int,
        business_tz: str,
    ) -> None:
        """Build and send weekly leaderboard message in HTML mode."""
        period = self._leaderboard_service.get_previous_calendar_week_period(
            business_tz=business_tz,
        )
        academic_rows = await self._leaderboard_service.get_previous_calendar_week_leaderboard(
            points_type=PointsTypeEnum.ACADEMIC,
            limit=limit,
            business_tz=business_tz,
        )
        reputation_rows = await self._leaderboard_service.get_previous_calendar_week_leaderboard(
            points_type=PointsTypeEnum.REPUTATION,
            limit=limit,
            business_tz=business_tz,
        )

        message = render_leaderboard_message(
            academic_rows=academic_rows,
            reputation_rows=reputation_rows,
            period=period,
        )
        await self._notification_port.send_message(
            NotifyDTO(
                recipient_id=recipient_id,
                message=message,
                parse_mode="HTML",
            )
        )
