from collections.abc import Sequence

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from ..core.constants import LevelTypeEnum
from ..db.models.user_module import Level, UserLevel

# from ..domain import Level


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


async def get_user_current_level(  # TODO Разбить это всё таки на две функции
    db: AsyncSession,
    user_id: int,
    points_type: LevelTypeEnum,
) -> tuple[UserLevel, Level] | None:
    """
    Возвращает кортеж (ORM-объект UserLevel, доменная Level)
    или None, если уровень не найден.
    """
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
    next_level_orm = result.scalar_one_or_none()

    if next_level_orm is None:
        return None

    return next_level_orm


async def get_previous_level(db: AsyncSession, current_level: Level, points_type: LevelTypeEnum) -> Level | None:
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
    prev_level_orm = result.scalar_one_or_none()

    if prev_level_orm is None:
        return None

    return prev_level_orm
