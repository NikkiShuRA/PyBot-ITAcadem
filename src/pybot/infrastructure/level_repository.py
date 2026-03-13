from collections.abc import Sequence

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from ..core.constants import LevelTypeEnum
from ..db.models.user_module import Level, UserLevel


class LevelRepository:
    async def get_all_levels(self, db: AsyncSession) -> Sequence[Level]:
        return await self.find_all_levels(db)

    async def find_all_levels(self, db: AsyncSession) -> Sequence[Level]:
        stmt = select(Level)
        result = await db.execute(stmt)
        return result.scalars().all()

    async def find_all_by_type(self, db: AsyncSession, points_type: str) -> Sequence[Level]:
        stmt = select(Level).where(Level.level_type == points_type)
        result = await db.execute(stmt)
        return result.scalars().all()

    async def get_all_by_type(self, db: AsyncSession, points_type: str) -> Sequence[Level]:
        return await self.find_all_by_type(db, points_type)

    async def find_initial_levels(self, db: AsyncSession) -> Sequence[Level]:
        stmt = select(Level).where(Level.required_points == 0)
        result = await db.execute(stmt)
        return result.scalars().all()

    async def get_initial_levels(self, db: AsyncSession) -> Sequence[Level]:
        return await self.find_initial_levels(db)

    async def level_exists(self, db: AsyncSession) -> bool:
        stmt = select(Level).limit(1)
        result = await db.execute(stmt)
        return result.scalars().first() is not None

    async def find_user_current_level(
        self,
        db: AsyncSession,
        user_id: int,
        points_type: LevelTypeEnum,
    ) -> tuple[UserLevel, Level] | None:
        stmt = (
            select(UserLevel)
            .options(joinedload(UserLevel.level))
            .join(Level)
            .where(
                UserLevel.user_id == user_id,
                Level.level_type == points_type,
            )
            .order_by(Level.required_points.desc())
            .limit(1)
        )
        result = await db.execute(stmt)
        user_level_orm: UserLevel | None = result.scalar_one_or_none()

        if user_level_orm is None or user_level_orm.level is None:
            return None

        return user_level_orm, user_level_orm.level

    async def find_next_level(
        self,
        db: AsyncSession,
        current_level: Level,
        points_type: LevelTypeEnum,
    ) -> Level | None:
        stmt = (
            select(Level)
            .where(
                Level.level_type == points_type,
                Level.required_points > current_level.required_points,
            )
            .order_by(Level.required_points.asc())
            .limit(1)
        )
        result = await db.execute(stmt)
        next_level_orm = result.scalar_one_or_none()

        if next_level_orm is None:
            return None

        return next_level_orm

    async def find_previous_level(
        self,
        db: AsyncSession,
        current_level: Level,
        points_type: LevelTypeEnum,
    ) -> Level | None:
        query = (
            select(Level)
            .where(Level.level_type == points_type, Level.required_points < current_level.required_points)
            .order_by(Level.required_points.desc())
            .limit(1)
        )
        result = await db.execute(query)
        prev_level_orm = result.scalar_one_or_none()

        if prev_level_orm is None:
            return None

        return prev_level_orm
