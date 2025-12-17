from ..core.constants import PointsTypeEnum
from .base import BaseEntityModel


class LevelEntity(BaseEntityModel):
    """Доменная сущность Уровня."""

    id: int
    name: str
    level_type: PointsTypeEnum
    description: str | None
    required_points: int
