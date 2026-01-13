from collections.abc import Sequence

from ..db.models import Level, UserLevel
from ..domain import LevelEntity


async def map_orm_level_to_domain(orm_level: Level) -> LevelEntity:
    """Маппит ORM Level объект в доменную LevelEntity."""
    return LevelEntity.model_validate(orm_level)


async def map_orm_levels_to_domain(orm_levels: Sequence[Level]) -> list[LevelEntity]:
    """Маппит список ORM Level объектов в список доменных LevelEntity."""
    return [await map_orm_level_to_domain(level) for level in orm_levels]


async def map_user_levels_to_domain_levels(user_levels_orm: Sequence[UserLevel]) -> list[LevelEntity]:
    """Маппит список UserLevel ORM объектов в список доменных LevelEntity."""
    return [LevelEntity.model_validate(ul.level) for ul in user_levels_orm]
