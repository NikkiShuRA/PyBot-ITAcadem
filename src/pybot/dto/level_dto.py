import re

from ..dto.value_objects import Points
from .base_dto import BaseDTO
from ..core.constants import LevelTypeEnum


class LevelReadDTO(BaseDTO):
    """
    DTO для отображения данных уровня.
    """

    system: LevelTypeEnum
    name: str
    required_points: Points