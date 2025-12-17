from collections.abc import Sequence

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from ..core.constants import PointsTypeEnum
from ..db.models.user_module import Level, UserLevel
from ..domain import LevelEntity


async def get_all_levels(db: AsyncSession) -> Sequence[LevelEntity]:
    """Получить все уровни из БД"""
    stmt = select(Level)
    result = await db.execute(stmt)
    return [
        LevelEntity(
            id=user_level_orm.id,
            name=user_level_orm.name,
            description=user_level_orm.description,
            required_points=user_level_orm.required_points,
            level_type=user_level_orm.level_type,
        )
        for user_level_orm in result.scalars().all()
    ]


async def level_exists(db: AsyncSession) -> bool:
    """Проверить, существуют ли уровни в БД"""
    stmt = select(Level).limit(1)
    result = await db.execute(stmt)
    return result.scalars().first() is not None


async def get_user_current_level(  # TODO Разбить это всё таки на две функции
    db: AsyncSession,
    user_id: int,
    points_type: PointsTypeEnum,
) -> tuple[UserLevel, LevelEntity] | None:
    """
    Возвращает кортеж (ORM-объект UserLevel, доменная LevelEntity)
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

    level_entity = LevelEntity(
        id=user_level_orm.level.id,
        name=user_level_orm.level.name,
        description=user_level_orm.level.description,
        required_points=user_level_orm.level.required_points,
        level_type=user_level_orm.level.level_type,
    )

    return user_level_orm, level_entity


async def get_next_level(
    db: AsyncSession,
    current_level: LevelEntity,
    points_type: PointsTypeEnum,
) -> LevelEntity | None:
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

    return LevelEntity(
        id=next_level_orm.id,
        name=next_level_orm.name,
        description=next_level_orm.description,
        required_points=next_level_orm.required_points,
        level_type=next_level_orm.level_type,
    )


async def get_previous_level(
    db: AsyncSession, current_level: LevelEntity, points_type: PointsTypeEnum
) -> LevelEntity | None:
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

    return LevelEntity(
        id=prev_level_orm.id,
        name=prev_level_orm.name,
        description=prev_level_orm.description,
        required_points=prev_level_orm.required_points,
        level_type=prev_level_orm.level_type,
    )
