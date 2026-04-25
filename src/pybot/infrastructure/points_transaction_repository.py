from collections.abc import Sequence
from datetime import UTC, datetime

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from ..core.constants import PointsTypeEnum
from ..db.models import PointsTransaction, User
from ..dto import WeeklyLeaderboardRowDTO


class PointsTransactionRepository:
    """Репозиторий для управления транзакциями баллов (PointsTransaction)."""

    async def add(self, db: AsyncSession, transaction: PointsTransaction) -> None:
        """Добавляет новую транзакцию в базу данных.

        Args:
            db: Асинхронная сессия базы данных.
            transaction: Обьект транзакции для добавления.
        """
        db.add(transaction)

    async def find_top_recipients_for_period(
        self,
        db: AsyncSession,
        *,
        points_type: PointsTypeEnum,
        period_start: datetime,
        period_end: datetime,
        limit: int = 10,
    ) -> Sequence[WeeklyLeaderboardRowDTO]:
        """Возвращает топ получателей с положительным чистым приростом баллов за период.

        Args:
            db: Асинхронная сессия базы данных.
            points_type: Тип баллов.
            period_start: Начало периода (timezone-aware).
            period_end: Конец периода (timezone-aware).
            limit: Максимальное количество строк в результате.

        Returns:
            Sequence[WeeklyLeaderboardRowDTO]: Список строк лидерборда.
        """
        start_at = period_start.astimezone(UTC).replace(tzinfo=None)
        end_at = period_end.astimezone(UTC).replace(tzinfo=None)

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
            # Показываем только тех, у кого чистый прирост за неделю положительный.
            # Вычеты снижают итоговый балл, но не выносят пользователя в топ.
            .having(total_points_delta > 0)
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
                period_start=period_start,
                period_end=period_end,
            )
            for row in rows
        ]
