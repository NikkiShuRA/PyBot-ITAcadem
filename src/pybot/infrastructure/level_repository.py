from collections.abc import Sequence

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..db.models.user_module import Level


class LevelRepository:
    async def get_all_levels(self, db: AsyncSession) -> Sequence[Level]:
        stmt = select(Level)
        result = await db.execute(stmt)
        return result.scalars().all()

    async def get_all_by_type(self, db: AsyncSession, points_type: str) -> Sequence[Level]:
        stmt = select(Level).where(Level.level_type == points_type)
        result = await db.execute(stmt)
        return result.scalars().all()

    async def get_initial_levels(self, db: AsyncSession) -> Sequence[Level]:
        stmt = select(Level).where(Level.required_points == 0)
        result = await db.execute(stmt)
        return result.scalars().all()
