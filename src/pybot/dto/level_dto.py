from ..dto.value_objects import Points
from .base_dto import BaseDTO


class LevelReadDTO(BaseDTO):
    """DTO для отображения данных уровня."""

    name: str
    required_points: Points
