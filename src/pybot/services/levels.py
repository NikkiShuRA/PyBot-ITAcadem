from collections.abc import Sequence

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from ..core.constants import LevelTypeEnum
from ..db.models.user_module import Level, UserLevel
from ..infrastructure import LevelRepository


class LevelService:
    def __init__(self, level_repo: LevelRepository, db: AsyncSession) -> None:
        self.level_repo = level_repo
        self.db = db

    async def find_all_levels(self) -> Sequence[Level]:
        return await self.level_repo.find_all_levels(self.db)

    async def level_exists(self) -> bool:
        return await self.level_repo.level_exists(self.db)

    async def find_user_current_level(
        self,
        user_id: int,
        points_type: LevelTypeEnum,
    ) -> tuple[UserLevel, Level] | None:
        return await self.level_repo.find_user_current_level(self.db, user_id, points_type)

    async def find_next_level(self, current_level: Level, points_type: LevelTypeEnum) -> Level | None:
        return await self.level_repo.find_next_level(self.db, current_level, points_type)

    async def find_previous_level(self, current_level: Level, points_type: LevelTypeEnum) -> Level | None:
        return await self.level_repo.find_previous_level(self.db, current_level, points_type)


async def get_all_levels(db: AsyncSession) -> Sequence[Level]:
    stmt = select(Level)
    result = await db.execute(stmt)
    return result.scalars().all()


async def level_exists(db: AsyncSession) -> bool:
    stmt = select(Level).limit(1)
    result = await db.execute(stmt)
    return result.scalars().first() is not None


async def get_user_current_level(
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


async def get_next_level(
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


async def get_previous_level(db: AsyncSession, current_level: Level, points_type: LevelTypeEnum) -> Level | None:
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
