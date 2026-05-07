from collections.abc import Sequence

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from ..core.constants import PointsTypeEnum
from ..db.models import Valuation


class ValuationRepository:
    """Репозиторий для управления операциями начисления баллов (Valuation)."""

    async def find_history_by_recipient(
        self,
        db: AsyncSession,
        recipient_id: int,
        points_type: PointsTypeEnum,
        limit: int = 10,
    ) -> Sequence[Valuation]:
        """Возвращает историю начислений баллов для указанного получателя.

        Args:
            db: Асинхронная сессия базы данных.
            recipient_id: ID пользователя-получателя.
            points_type: Тип баллов.
            limit: Максимальное количество записей.

        Returns:
            Sequence[Valuation]: Список записей истории начислений.
        """
        stmt = (
            select(Valuation)
            .options(selectinload(Valuation.giver))
            .where(Valuation.recipient_id == recipient_id)
            .where(Valuation.points_type == points_type)
            .order_by(Valuation.created_at.desc())
            .limit(limit)
        )

        result = await db.execute(stmt)
        return result.scalars().all()
