from datetime import date
from typing import Annotated

from pydantic import Field, field_validator

from ..core.constants import PointsTypeEnum
from ..db.models.user_module import UserLevel
from .base_dto import BaseDTO


class AdjustUserPointsDTO(BaseDTO):
    """Data transfer object for adjusting a user's points.

    This bundles the parameters previously passed as many separate
    arguments to `adjust_user_points` into a single validated object.
    """

    recipient_id: int
    giver_id: int
    points: Annotated[int, Field(strict=True, ge=-(2**31), le=2**31 - 1)]
    points_type: PointsTypeEnum
    reason: str | None = None


class UserCreateDTO(BaseDTO):
    """DTO для создания нового пользователя."""

    phone: str
    tg_id: int
    first_name: str = Field(..., min_length=1, max_length=100)
    last_name: str | None = Field(None, min_length=1, max_length=100)
    patronymic: str | None = Field(None, min_length=1, max_length=100)

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
            return v.strip()
        return v


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
    academic_points: int
    reputation_points: int
    join_date: date


class UpdateUserLevelDTO(BaseDTO):
    """DTO for updating a user's level.

    This bundles the parameters previously passed as many separate
    arguments to `update_user_level` into a single validated object.
    """

    user: UserReadDTO
    user_level: UserLevel
    points_type: PointsTypeEnum
    current_points: int
    inputed_points: int
