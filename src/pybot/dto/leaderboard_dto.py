"""DTO для построения и отображения таблиц лидеров."""

from dataclasses import dataclass
from datetime import datetime

from pydantic import AwareDatetime, computed_field

from ..core.constants import PointsTypeEnum
from .base_dto import BaseDTO


# Timezone-aware datetime, гарантирует наличие tzinfo на уровне типизации.
@dataclass(slots=True, frozen=True)
class LeaderboardPeriod:
    """Период для отображения в таблице лидеров.

    Обе даты должны быть timezone-aware и находиться в одном бизнес-часовом поясе.
    Используется только для форматирования периода в пользовательском сообщении;
    не совпадает с UTC-границами SQL-запроса.
    """

    start: datetime
    end: datetime


class WeeklyLeaderboardRowDTO(BaseDTO):
    """DTO строки еженедельной таблицы лидеров для конкретного пользователя.

    ``period_start`` и ``period_end`` хранятся в бизнес-часовом поясе
    (timezone-aware) и используются исключительно для отображения периода.
    Они не совпадают с UTC-границами, которые применяются в SQL-запросе.
    """

    user_id: int
    telegram_id: int
    first_name: str
    last_name: str | None
    patronymic: str | None
    total_points_delta: int
    points_type: PointsTypeEnum
    period_start: AwareDatetime
    period_end: AwareDatetime

    @computed_field
    @property
    def display_name(self) -> str:
        """Возвращает полное имя пользователя в удобном для чтения формате."""
        name_parts = [
            self.last_name,
            self.first_name,
            self.patronymic,
        ]
        return " ".join(part for part in name_parts if part)
