from typing import TYPE_CHECKING

from .base import BaseEntityModel

if TYPE_CHECKING:
    from ..domain import UserEntity, LevelSystemEntity  

class UserLevelStateEntity(BaseEntityModel):
    """Доменная сущность Уровня пользователя."""

    id: int
    user: UserEntity
    level_system: LevelSystemEntity
    points: int