from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field

from ..core.constants import PointsTypeEnum


class BaseValueModel(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)


class Points(BaseValueModel):
    """
    Класс для представления количества очков.

    Attributes:
        value (int): Количество очков.
        point_type (Points_type_enum): Тип очков.

    Methods:
        adjust (int): Меняет количество очков на заданное значение.

    Returns:
        Points: Новый объект Points с измененным количеством очков.

    """

    value: Annotated[int, Field(strict=True, ge=-(2**31), le=2**31 - 1)]
    point_type: PointsTypeEnum

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
        return f"{self.value} {type_name}"

    def __repr__(self) -> str:
        return f"Points(value={self.value}, point_type={self.point_type})"

    def __ge__(self, other: "Points" | int) -> bool:
        val = other.value if isinstance(other, Points) else other
        return self.value >= val

    def __lt__(self, other: "Points" | int) -> bool:
        val = other.value if isinstance(other, Points) else other
        return self.value < val

    def __add__(self, other: "Points" | int) -> "Points":
        val = other.value if isinstance(other, Points) else other
        return Points(value=self.value + val, point_type=self.point_type)

        if isinstance(other, int):
            return self.adjust(other)

        if isinstance(other, Points):
            if self.point_type != other.point_type:
                raise ValueError(f"Cannot add {other.point_type} to {self.point_type}")
            return self.adjust(other.value)

        raise NotImplementedError(f"Addition not supported between Points and {type(other)}")

    def __sub__(self, other: "Points" | int) -> "Points":
        if isinstance(other, int):
            return self.adjust(-other)

        if isinstance(other, Points):
            if self.point_type != other.point_type:
                raise ValueError(f"Cannot subtract {other.point_type} from {self.point_type}")
            return self.adjust(-other.value)

        raise NotImplementedError(f"Subtraction not supported between Points and {type(other)}")
