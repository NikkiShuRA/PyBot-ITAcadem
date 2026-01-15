from collections.abc import Sequence

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

# from ..core.constants import PointsTypeEnum
from ..db.models import Level, UserLevelState, LevelSystem
from ..domain import LevelEntity
from ..mappers.level_mappers import map_orm_level_to_domain, map_orm_levels_to_domain


async def get_all_levels(db: AsyncSession) -> Sequence[LevelEntity]:
    """Получить все уровни из БД"""
    stmt = select(Level)
    result = await db.execute(stmt)
    return await map_orm_levels_to_domain(result.scalars().all())


async def level_exists(db: AsyncSession) -> bool:
    """Проверить, существуют ли уровни в БД"""
    stmt = select(Level).limit(1)
    result = await db.execute(stmt)
    return result.scalars().first() is not None


async def get_user_current_level(  # TODO Разбить это всё таки на две функции
    db: AsyncSession,
    user_id: int,
    level_system_type: LevelSystem,
) -> tuple[UserLevelState, LevelEntity] | None:
    """
    Возвращает кортеж (ORM-объект UserLevel, доменная LevelEntity)
    или None, если уровень не найден.
    """
    stmt = (
        select(UserLevelState)
        .options(joinedload(UserLevelState.level))
        .join(Level)
        .where(
            UserLevelState.user_id == user_id,
            Level.level_system_id == level_system_type,
        )
        .order_by(Level.required_points.desc())
        .limit(1)
    )
    result = await db.execute(stmt)
    user_level_state_orm: UserLevelState | None = result.scalar_one_or_none()

    if user_level_state_orm is None or user_level_state_orm.level is None:
        return None

    level_entity = await map_orm_level_to_domain(user_level_state_orm.level)

    return user_level_state_orm, level_entity


async def get_next_level(
    db: AsyncSession,
    current_level: LevelEntity,
    level_system_type: LevelSystem,
) -> LevelEntity | None:
    """Получить следующий уровень для повышения"""
    stmt = (
        select(Level)
        .where(
            Level.level_type == level_system_type,
            Level.required_points > current_level.required_points,
        )
        .order_by(Level.required_points.asc())
        .limit(1)
    )
    result = await db.execute(stmt)
    next_level_orm = result.scalar_one_or_none()

    if next_level_orm is None:
        return None

    return await map_orm_level_to_domain(next_level_orm)


async def get_previous_level(
    db: AsyncSession, current_level: LevelEntity, level_system_type: LevelSystem
) -> LevelEntity | None:
    """
    Находит предыдущий уровень для заданного типа баллов.
    Предполагается, что уровни можно отсортировать по 'required_points'.
    """
    query = (
        select(Level)
        .where(Level.level_type == level_system_type, Level.required_points < current_level.required_points)
        .order_by(Level.required_points.desc())  # Сортируем по убыванию, чтобы найти ближайший меньший
        .limit(1)
    )
    result = await db.execute(query)
    prev_level_orm = result.scalar_one_or_none()

    if prev_level_orm is None:
        return None

    return await map_orm_level_to_domain(prev_level_orm)
