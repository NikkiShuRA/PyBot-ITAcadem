from collections.abc import Sequence
from datetime import datetime

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from ..core.constants import PointsTypeEnum
from ..db.models import PointsTransaction, User
from ..dto import WeeklyLeaderboardRowDTO


class PointsTransactionRepository:
    async def add(self, db: AsyncSession, transaction: PointsTransaction) -> None:
        db.add(transaction)

    async def find_top_recipients_for_period(
        self,
        db: AsyncSession,
        *,
        points_type: PointsTypeEnum,
        start_at: datetime,
        end_at: datetime,
        limit: int = 10,
    ) -> Sequence[WeeklyLeaderboardRowDTO]:
        total_points_delta = func.sum(PointsTransaction.amount).label("total_points_delta")
        stmt = (
            select(
                User.id,
                User.telegram_id,
                User.first_name,
                User.last_name,
                User.patronymic,
                total_points_delta,
            )
            .join(PointsTransaction, PointsTransaction.recipient_id == User.id)
            .where(
                PointsTransaction.points_type == points_type,
                PointsTransaction.created_at >= start_at,
                PointsTransaction.created_at < end_at,
            )
            .group_by(
                User.id,
                User.first_name,
                User.last_name,
                User.patronymic,
            )
            .order_by(total_points_delta.desc(), User.id.asc())
            .limit(limit)
        )

        result = await db.execute(stmt)
        rows = result.all()

        return [
            WeeklyLeaderboardRowDTO(
                user_id=row.id,
                telegram_id=row.telegram_id,
                first_name=row.first_name,
                last_name=row.last_name,
                patronymic=row.patronymic,
                total_points_delta=row.total_points_delta,
                points_type=points_type,
                period_start=start_at,
                period_end=end_at,
            )
            for row in rows
        ]
