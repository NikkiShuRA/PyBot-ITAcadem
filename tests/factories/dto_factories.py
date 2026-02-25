from __future__ import annotations

from itertools import count, cycle

from polyfactory.factories.pydantic_factory import ModelFactory

from pybot.core.constants import LevelTypeEnum
from pybot.dto import AdjustUserPointsDTO, UserCreateDTO
from pybot.dto.value_objects import Points

_points_value_seq = cycle((-50, 0, 150))
_points_type_seq = cycle((LevelTypeEnum.ACADEMIC, LevelTypeEnum.REPUTATION))
_tg_id_seq = count(100_000)


def next_points_value() -> int:
    return next(_points_value_seq)


def next_points_type() -> LevelTypeEnum:
    return next(_points_type_seq)


def next_tg_id() -> int:
    return next(_tg_id_seq)


def default_academic_points() -> Points:
    return Points(value=10, point_type=LevelTypeEnum.ACADEMIC)


class PointsFactory(ModelFactory[Points]):
    __model__ = Points

    value = next_points_value
    point_type = next_points_type


class UserCreateDTOFactory(ModelFactory[UserCreateDTO]):
    __model__ = UserCreateDTO

    phone = "+79876543210"
    tg_id = next_tg_id
    first_name = "Ivan"
    last_name = "Petrov"
    patronymic = "Sergeevich"


class AdjustUserPointsDTOFactory(ModelFactory[AdjustUserPointsDTO]):
    __model__ = AdjustUserPointsDTO

    recipient_id = 1
    giver_id = 2
    points = default_academic_points
    reason = "Great work"
