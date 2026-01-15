from datetime import date
from typing import TYPE_CHECKING, Optional

from pydantic import Field

from .base import BaseEntityModel
# from .factories import default_academic_points, default_reputation_points

if TYPE_CHECKING:
    from ..domain import UserLevelStateEntity, RoleEntity, TaskEntity


class UserEntity(BaseEntityModel):
    """Доменная сущность Пользователя."""

    id: int
    first_name: str
    last_name: str
    patronymic: str | None
    telegram_id: int
    
    join_date: date

    user_level_states: list["UserLevelStateEntity"] = Field(default_factory=list)
    # academic_points: Annotated[Points, Field(default_factory=default_academic_points)]
    # reputation_points: Annotated[Points, Field(default_factory=default_reputation_points)]
    
    role: Optional["RoleEntity"] = None

    created_tasks: list["TaskEntity"] = Field(default_factory=list)

    solutions: list["TaskEntity"] = Field(default_factory=list)
