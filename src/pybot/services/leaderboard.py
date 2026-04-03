from collections.abc import Sequence

import pendulum
from sqlalchemy.ext.asyncio import AsyncSession

from ..core.constants import PointsTypeEnum
from ..dto import WeeklyLeaderboardRowDTO
from ..infrastructure import PointsTransactionRepository


class LeaderboardService:
    def __init__(
        self,
        db: AsyncSession,
        points_transaction_repository: PointsTransactionRepository,
    ) -> None:
        self.db = db
        self.points_transaction_repository = points_transaction_repository

    async def get_previous_calendar_week_leaderboard(
        self,
        *,
        points_type: PointsTypeEnum,
        limit: int = 10,
        business_tz: str = "Asia/Yekaterinburg",
    ) -> Sequence[WeeklyLeaderboardRowDTO]:
        now = pendulum.now(business_tz)
        start_local = now.start_of("week").subtract(weeks=1)
        end_local = start_local.add(weeks=1)

        start_at = start_local.in_timezone("UTC").naive()
        end_at = end_local.in_timezone("UTC").naive()

        return await self.points_transaction_repository.find_top_recipients_for_period(
            self.db,
            points_type=points_type,
            start_at=start_at,
            end_at=end_at,
            limit=limit,
        )
