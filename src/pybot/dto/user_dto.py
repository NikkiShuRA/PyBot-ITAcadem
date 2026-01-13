import re
from datetime import date
from typing import ClassVar

from pydantic import Field, field_validator

from ..domain import Points
from ..utils import normalize_phone
from .base_dto import BaseDTO


class AdjustUserPointsDTO(BaseDTO):
    """Data transfer object for adjusting a user's points.

    This bundles the parameters previously passed as many separate
    arguments to `adjust_user_points` into a single validated object.
    """

    recipient_id: int
    giver_id: int
    points: Points
    reason: str | None = None


class UserCreateDTO(BaseDTO):
    """DTO для создания нового пользователя."""

    NAME_MIN_LENGTH: ClassVar[int] = 1
    NAME_MAX_LENGTH: ClassVar[int] = 100

    phone: str
    tg_id: int
    first_name: str = Field(..., min_length=NAME_MIN_LENGTH, max_length=NAME_MAX_LENGTH)
    last_name: str = Field(..., min_length=NAME_MIN_LENGTH, max_length=NAME_MAX_LENGTH)
    patronymic: str | None = Field(None, min_length=NAME_MIN_LENGTH, max_length=NAME_MAX_LENGTH)

    @field_validator("first_name", "last_name", "patronymic")
    @classmethod
    def clean_string(cls, v: str | None) -> str | None:
        """Clean a string by stripping whitespace.

        This is a helper function for validating UserCreateDTO fields.
        It is used as a field validator to clean strings passed in the
        UserCreateDTO. If the string is None, it is returned unchanged.
        Otherwise, it is stripped of leading and trailing whitespace.

        :param v: The string to clean.
        :return: The cleaned string, or None if the string was None.
        """
        if v is not None:
            v = re.sub(r"[^а-яА-Я\s]", "", v)
            v = v.strip()

        return v

    @field_validator("phone")
    @classmethod
    def normalize_phone(cls, v: str) -> str:
        return normalize_phone(v)


class UserReadDTO(BaseDTO):
    """
    DTO для отображения данных пользователя.

    Атрибуты:
        id (int): Идентификатор пользователя.
        first_name (str): Имя пользователя.
        last_name (str | None): Фамилия пользователя.
        patronymic (str | None): Отчество пользователя.
        telegram_id (int): Идентификатор пользователя в Telegram.
        academic_points (int): Академические баллы пользователя.
        reputation_points (int): Баллы репутации пользователя.
        join_date (date): Дата присоединения пользователя.
    """

    id: int
    first_name: str
    last_name: str | None
    patronymic: str | None
    telegram_id: int
    academic_points: Points
    reputation_points: Points
    join_date: date


class UpdateUserLevelDTO(BaseDTO):
    """DTO for updating a user's level.

    This bundles the parameters previously passed as many separate
    arguments to `update_user_level` into a single validated object.
    """

    user: UserReadDTO
    current_points: Points
    inputed_points: Points
