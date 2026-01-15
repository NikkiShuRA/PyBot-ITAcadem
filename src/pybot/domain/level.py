from typing import TYPE_CHECKING

from .base import BaseEntityModel

if TYPE_CHECKING:
    from ..domain import LevelSystemEntity

class LevelEntity(BaseEntityModel):
    """Доменная сущность Уровня."""

    id: int
    name: str
    level_system: LevelSystemEntity
    description: str | None
    required_points: int
