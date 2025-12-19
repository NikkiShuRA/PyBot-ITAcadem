from ..db.models import User
from ..domain import LevelEntity
from .level_mappers import map_user_levels_to_domain_levels


async def map_orm_levels_to_domain(user: User) -> list[LevelEntity] | None:
    """
    Маппит список ORM Level объектов в список доменных LevelEntity.
    Если пользователь не найден или не имеет связанных уровней, возвращает None.
    """

    if user and hasattr(user, "user_levels"):
        return await map_user_levels_to_domain_levels(user.user_levels)
    else:
        return None
