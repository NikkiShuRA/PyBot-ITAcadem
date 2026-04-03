from datetime import datetime

from pydantic import computed_field

from ..core.constants import PointsTypeEnum
from .base_dto import BaseDTO


class WeeklyLeaderboardRowDTO(BaseDTO):
    user_id: int
    telegram_id: int
    first_name: str
    last_name: str | None
    patronymic: str | None
    total_points_delta: int
    points_type: PointsTypeEnum
    period_start: datetime
    period_end: datetime

    @computed_field
    @property
    def display_name(self) -> str:
        name_parts = [
            self.last_name,
            self.first_name,
            self.patronymic,
        ]
        return " ".join(part for part in name_parts if part)
