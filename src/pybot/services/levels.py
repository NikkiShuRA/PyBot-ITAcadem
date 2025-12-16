from collections.abc import Sequence

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..core.constants import PointsTypeEnum
from ..db.models.user_module import Level, UserLevel


async def get_all_levels(db: AsyncSession) -> Sequence[Level]:
    """Получить все уровни из БД"""
    stmt = select(Level)
    result = await db.execute(stmt)
    return result.scalars().all()


async def level_exists(db: AsyncSession) -> bool:
    """Проверить, существуют ли уровни в БД"""
    stmt = select(Level).limit(1)
    result = await db.execute(stmt)
    return result.scalars().first() is not None


async def get_user_current_level(
    db: AsyncSession,
    user_id: int,
    points_type: PointsTypeEnum,
) -> UserLevel | None:
    """Получить текущий уровень пользователя для типа баллов"""
    stmt = (
        select(UserLevel)
        .join(Level)
        .where(UserLevel.user_id == user_id, Level.level_type == points_type)
        .order_by(Level.required_points.desc())
        .limit(1)
    )
    result = await db.execute(stmt)
    return result.scalar_one_or_none()


async def get_next_level(
    db: AsyncSession,
    current_level: Level,
    points_type: PointsTypeEnum,
) -> Level | None:
    """Получить следующий уровень для повышения"""
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
    return result.scalar_one_or_none()


async def get_previous_level(db: AsyncSession, current_level: Level, points_type: PointsTypeEnum) -> Level | None:
    """
    Находит предыдущий уровень для заданного типа баллов.
    Предполагается, что уровни можно отсортировать по 'required_points'.
    """
    query = (
        select(Level)
        .where(Level.level_type == points_type, Level.required_points < current_level.required_points)
        .order_by(Level.required_points.desc())  # Сортируем по убыванию, чтобы найти ближайший меньший
        .limit(1)
    )
    result = await db.execute(query)
    return result.scalars().first()


async def get_level_by_id(db: AsyncSession, level_id: int) -> Level | None:
    """Получить уровень по ID"""
    stmt = select(Level).where(Level.id == level_id)
    result = await db.execute(stmt)
    return result.scalar_one_or_none()
