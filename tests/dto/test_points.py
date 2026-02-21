import random
from typing import Any

import pytest
from polyfactory.factories.pydantic_factory import ModelFactory

from pybot.core.constants import LevelTypeEnum
from pybot.dto.value_objects import Points


class PointsFactory(ModelFactory[Points]):
    __model__ = Points

    # Генерируем реалистичные значения
    value = lambda: random.randint(-2_147_483_648, 2_147_483_647)
    point_type = lambda: random.choice([LevelTypeEnum.ACADEMIC, LevelTypeEnum.REPUTATION])


@pytest.fixture
def academic_100() -> Points:
    return Points(value=100, point_type=LevelTypeEnum.ACADEMIC)


@pytest.fixture
def reputation_50() -> Points:
    return Points(value=50, point_type=LevelTypeEnum.REPUTATION)


@pytest.fixture
def zero_points() -> Points:
    return Points(value=0, point_type=LevelTypeEnum.ACADEMIC)


# ==================== Инициализация ====================


def test_points_can_be_created_with_valid_values():
    p = Points(value=500, point_type=LevelTypeEnum.ACADEMIC)
    assert p.value == 500
    assert p.point_type == LevelTypeEnum.ACADEMIC


@pytest.mark.parametrize("value", [-2_147_483_648, 0, 2_147_483_647])
def test_points_accepts_boundary_int32_values(value: int):
    p = Points(value=value, point_type=LevelTypeEnum.REPUTATION)
    assert p.value == value


def test_points_raises_on_too_large_value():
    with pytest.raises(Exception):  # pydantic ValidationError
        Points(value=2_147_483_648, point_type=LevelTypeEnum.ACADEMIC)


# ==================== Семантические методы ====================


def test_is_positive(academic_100: Points, zero_points: Points):
    assert academic_100.is_positive() is True
    assert zero_points.is_positive() is False


def test_is_negative(reputation_50: Points, zero_points: Points):
    assert Points(value=-10, point_type=LevelTypeEnum.ACADEMIC).is_negative() is True
    assert zero_points.is_negative() is False


def test_is_negative_delta():
    p = Points(value=100, point_type=LevelTypeEnum.ACADEMIC)
    assert p.is_negative_delta(-5) is True
    assert p.is_negative_delta(0) is False
    assert p.is_negative_delta(10) is False


# ==================== Сравнения ====================


def test_compare_to_threshold():
    p = Points(value=150, point_type=LevelTypeEnum.ACADEMIC)
    assert p.compare_to_threshold(100) is True
    assert p.compare_to_threshold(150) is True
    assert p.compare_to_threshold(200) is False


def test_compare_to_past_threshold():
    p = Points(value=80, point_type=LevelTypeEnum.REPUTATION)
    assert p.compare_to_past_threshold(100) is True
    assert p.compare_to_past_threshold(80) is False


def test_ge_operator_with_int_and_points(academic_100: Points):
    assert academic_100 >= 50
    assert academic_100 >= 100
    assert not (academic_100 >= 150)

    other = Points(value=80, point_type=LevelTypeEnum.ACADEMIC)
    assert academic_100 >= other


def test_lt_operator_with_int_and_points(academic_100: Points):
    assert academic_100 < 150
    assert not (academic_100 < 100)

    other = Points(value=120, point_type=LevelTypeEnum.ACADEMIC)
    assert academic_100 < other


# ==================== Арифметика ====================


def test_adjust_returns_new_instance(academic_100: Points):
    p2 = academic_100.adjust(50)
    assert p2 is not academic_100
    assert p2.value == 150
    assert p2.point_type == academic_100.point_type


def test_add_with_int(academic_100: Points):
    result = academic_100 + 50
    assert result.value == 150
    assert result.point_type == LevelTypeEnum.ACADEMIC


def test_add_with_same_type_points(reputation_50: Points):
    p2 = Points(value=30, point_type=LevelTypeEnum.REPUTATION)
    result = reputation_50 + p2
    assert result.value == 80
    assert result.point_type == LevelTypeEnum.REPUTATION


def test_add_with_different_type_raises():
    p1 = Points(value=100, point_type=LevelTypeEnum.ACADEMIC)
    p2 = Points(value=50, point_type=LevelTypeEnum.REPUTATION)

    with pytest.raises(ValueError):
        p1 + p2


def test_sub_with_int(academic_100: Points):
    result = academic_100 - 30
    assert result.value == 70


def test_sub_with_same_type(reputation_50: Points):
    p2 = Points(value=20, point_type=LevelTypeEnum.REPUTATION)
    result = reputation_50 - p2
    assert result.value == 30


# ==================== Равенство и хэш ====================


def test_eq_depends_on_value_and_type():
    p1 = Points(value=100, point_type=LevelTypeEnum.ACADEMIC)
    p2 = Points(value=100, point_type=LevelTypeEnum.ACADEMIC)
    p3 = Points(value=100, point_type=LevelTypeEnum.REPUTATION)
    p4 = Points(value=200, point_type=LevelTypeEnum.ACADEMIC)

    assert p1 == p2
    assert p1 != p3
    assert p1 != p4
    assert p1 != 100  # не равен int


def test_hash_consistent_with_eq():
    p1 = Points(value=100, point_type=LevelTypeEnum.ACADEMIC)
    p2 = Points(value=100, point_type=LevelTypeEnum.ACADEMIC)

    assert hash(p1) == hash(p2)
    d = {p1: "value"}
    assert d[p2] == "value"


# ==================== Строковое представление ====================


def test_str_and_repr(academic_100: Points):
    assert str(academic_100) == "100 academic"
    assert "value=100" in repr(academic_100)
    assert "point_type=academic" in repr(academic_100)
