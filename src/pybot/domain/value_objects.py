from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field

from .level_system import LevelSystemEntity


class BaseValueModel(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)


class Points(BaseValueModel):
    """
    Класс для представления количества очков.

    Attributes:
        value (int): Количество очков.
        pointlevel_system_type_type (LevelSystemEntity): Тип системы уровня.

    Methods:
        adjust (int): Меняет количество очков на заданное значение.

    Returns:
        Points: Новый объект Points с измененным количеством очков.

    """

    value: Annotated[int, Field(strict=True, ge=-(2**31), le=2**31 - 1)]
    level_system_type: LevelSystemEntity

    def adjust(self, delta: int) -> "Points":
        """
        Меняет количество очков на заданное значение.

        Args:
            delta (int): Заданное изменение количества очков.

        Returns:
            Points: Новый объект Points с измененным количеством очков.

        """

        new_value = self.value + delta
        return Points(value=new_value, point_type=self.point_type)

    def is_positive(self) -> bool:
        """Семантика: value > 0?"""
        return self.value > 0

    def is_negative(self) -> bool:
        """Семантика: value < 0?"""
        return self.value < 0

    def is_negative_delta(self, delta: int) -> bool:
        """Семантика: delta < 0?"""
        return delta < 0

    def compare_to_threshold(self, threshold: int) -> bool:
        """Семантика: value >= threshold?"""
        return self.value >= threshold

    def compare_to_past_threshold(self, threshold: int) -> bool:
        """Семантика: value < threshold?"""
        return self.value < threshold

    def __eq__(self, other: object) -> bool:
        if isinstance(other, Points):
            return self.value == other.value and self.point_type == other.point_type
        return False

    def __hash__(self) -> int:
        return hash((self.value, self.point_type))

    def __str__(self) -> str:
        type_name = self.point_type.value.lower()
        return f"{self.value} {type_name})"

    def __repr__(self) -> str:
        return f"Points(value={self.value}, point_type={self.point_type})"
