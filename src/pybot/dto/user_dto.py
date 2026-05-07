"""DTO для работы с профилями пользователей, уровнями и достижениями."""

import re
from collections.abc import Sequence
from datetime import date
from typing import ClassVar

from pydantic import Field, computed_field, field_validator

from ..core.constants import PointsTypeEnum
from ..domain.exceptions import InvalidPhoneNumberError, NameInputValidationError
from ..dto.value_objects import Points
from ..utils import normalize_phone, progress_bar
from .base_dto import BaseDTO
from .competence_dto import CompetenceReadDTO
from .level_dto import LevelReadDTO


class AdjustUserPointsDTO(BaseDTO):
    """DTO для корректировки баллов пользователя (начисления или списания).

    Объединяет параметры изменения баллов в единый валидируемый объект.
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
        """Очищает строку от нежелательных символов и пробелов.

        Данная функция удаляет все символы, не являющиеся русскими буквами
        или пробелами. Убирает лишние пробелы в начале и в конце строки.

        Args:
            v (str | None): Строка для очистки.

        Returns:
            str | None: Очищенная строка или None, если на вход передан None.
        """
        if v is not None:
            v = re.sub(r"[^а-яА-Я\s]", "", v)
            v = v.strip()

        return v

    @classmethod
    def validate_name_input(
        cls,
        raw_text: str,
        *,
        allow_empty: bool = False,
    ) -> str | None:
        """Валидирует пользовательский ввод имени с использованием контрактов DTO."""
        text = raw_text.strip()
        if not text:
            if allow_empty:
                return None
            raise NameInputValidationError("empty")

        cleaned_text = cls.clean_string(text)
        if cleaned_text != text:
            raise NameInputValidationError("invalid_symbols")

        if len(text) < cls.NAME_MIN_LENGTH:
            raise NameInputValidationError("too_short")

        if len(text) > cls.NAME_MAX_LENGTH:
            raise NameInputValidationError("too_long", max_length=cls.NAME_MAX_LENGTH)

        return text

    @field_validator("phone")
    @classmethod
    def normalize_phone(cls, v: str) -> str:
        """Нормализует формат номера телефона."""
        try:
            return normalize_phone(v)
        except ValueError as e:
            raise InvalidPhoneNumberError(v, str(e)) from e


class UserReadDTO(BaseDTO):
    """DTO для отображения данных пользователя.

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
    """DTO для обновления уровня пользователя.

    Объединяет параметры, необходимые для расчета и применения нового
    академического уровня, в единый валидируемый объект.
    """

    user: UserReadDTO
    current_points: Points
    inputed_points: Points


class UserLevelReadDTO(BaseDTO):
    """DTO для отображения прогресса уровня пользователя."""

    current_level: LevelReadDTO
    next_level: LevelReadDTO


class UserProfileReadDTO(BaseDTO):
    """DTO для отображения расширенного списка данных пользователя."""

    user: UserReadDTO
    competences: Sequence[CompetenceReadDTO]
    roles: Sequence[str]
    level_info: dict[PointsTypeEnum, UserLevelReadDTO]


class UserRegistrationDTO(BaseDTO):
    """DTO со входными данными для процесса регистрации студента."""

    user: UserCreateDTO
    competence_ids: Sequence[int] = Field(default_factory=tuple)


class ProfileViewDTO(BaseDTO):
    """DTO для подготовки данных профиля пользователя перед отображением."""

    user: UserReadDTO

    academic_progress: Points
    academic_level: UserLevelReadDTO
    academic_current_points: Points
    academic_next_points: Points

    reputation_progress: Points
    reputation_level: UserLevelReadDTO
    reputation_current_points: Points
    reputation_next_points: Points

    roles_data: Sequence[str]

    competences: Sequence[CompetenceReadDTO]

    @computed_field
    @property
    def academic_progress_bar(self) -> str:
        """Генерирует строку индикатора прогресса (прогресс-бар) для академических баллов."""
        return progress_bar(self.academic_current_points.value, self.academic_next_points.value)

    @computed_field
    @property
    def reputation_progress_bar(self) -> str:
        """Генерирует строку индикатора прогресса (прогресс-бар) для баллов репутации."""
        return progress_bar(self.reputation_current_points.value, self.reputation_next_points.value)
