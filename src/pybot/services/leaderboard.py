from collections.abc import Sequence
from datetime import datetime
from zoneinfo import ZoneInfo

import pendulum
from sqlalchemy.ext.asyncio import AsyncSession

from ..core.constants import PointsTypeEnum
from ..dto import WeeklyLeaderboardRowDTO
from ..dto.leaderboard_dto import LeaderboardPeriod
from ..infrastructure import PointsTransactionRepository


class LeaderboardService:
    def __init__(
        self,
        db: AsyncSession,
        points_transaction_repository: PointsTransactionRepository,
    ) -> None:
        self.db = db
        self.points_transaction_repository = points_transaction_repository

    def get_previous_calendar_week_period(
        self,
        *,
        business_tz: str = "Asia/Yekaterinburg",
    ) -> LeaderboardPeriod:
        """Вернуть timezone-aware период предыдущей календарной недели в бизнес-TZ."""
        now = pendulum.now(business_tz)
        start_local = now.start_of("week").subtract(weeks=1)
        end_local = start_local.add(weeks=1)

        business_timezone = ZoneInfo(business_tz)
        return LeaderboardPeriod(
            start=datetime.fromtimestamp(start_local.timestamp(), tz=business_timezone),
            end=datetime.fromtimestamp(end_local.timestamp(), tz=business_timezone),
        )

    async def get_previous_calendar_week_leaderboard(
        self,
        *,
        points_type: PointsTypeEnum,
        limit: int = 10,
        business_tz: str = "Asia/Yekaterinburg",
    ) -> Sequence[WeeklyLeaderboardRowDTO]:
        """Вернуть топ получателей за предыдущую календарную неделю.

        Период рассчитывается в бизнес-часовом поясе ``business_tz``.
        SQL-границы конвертируются в UTC-naive для совместимости с SQLite.
        Display-даты остаются timezone-aware в бизнес-TZ и передаются в DTO
        для корректного отображения пользователю.
        """
        period = self.get_previous_calendar_week_period(business_tz=business_tz)

        return await self.points_transaction_repository.find_top_recipients_for_period(
            self.db,
            points_type=points_type,
            period_start=period.start,
            period_end=period.end,
            limit=limit,
        )
