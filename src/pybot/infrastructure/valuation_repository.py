from collections.abc import Sequence

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from ..core.constants import LevelTypeEnum
from ..db.models import Valuation


class ValuationRepository:
    """
    Отвечает за доступ к операциям с баллами (Valuation).
    """

    async def get_history_by_recipient(
        self,
        db: AsyncSession,
        recipient_id: int,
        points_type: LevelTypeEnum,
        limit: int = 10,
    ) -> Sequence[Valuation]:
        """
        Возвращает последние N записей о начислении баллов для конкретного студента.
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
