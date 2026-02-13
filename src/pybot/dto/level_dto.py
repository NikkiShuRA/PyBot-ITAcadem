from ..core.constants import LevelTypeEnum
from ..dto.value_objects import Points
from .base_dto import BaseDTO


class LevelReadDTO(BaseDTO):
    """
    DTO для отображения данных уровня.
    """

    system: LevelTypeEnum
    name: str
    required_points: Points
