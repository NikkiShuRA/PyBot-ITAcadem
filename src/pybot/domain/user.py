from datetime import date
from typing import TYPE_CHECKING, Annotated

from pydantic import Field

from .base import BaseEntityModel
from .factories import default_academic_points, default_reputation_points
from .value_objects import Points

if TYPE_CHECKING:
    from .achievement import AchievementEntity
    from .competence import CompetenceEntity
    from .level import LevelEntity
    from .task import TaskEntity


class UserEntity(BaseEntityModel):
    """Доменная сущность Пользователя."""

    id: int
    first_name: str
    last_name: str | None
    patronymic: str | None
    telegram_id: int
    academic_points: Annotated[Points, Field(default_factory=default_academic_points)]
    reputation_points: Annotated[Points, Field(default_factory=default_reputation_points)]
    join_date: date

    user_levels: list["LevelEntity"] = Field(default_factory=list)

    competencies: list["CompetenceEntity"] = Field(default_factory=list)
    achievements: list["AchievementEntity"] = Field(default_factory=list)

    created_tasks: list["TaskEntity"] = Field(default_factory=list)

    solutions: list["TaskEntity"] = Field(default_factory=list)
