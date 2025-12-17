from datetime import date
from typing import TYPE_CHECKING, Optional

from pydantic import Field

from .base import BaseEntityModel

if TYPE_CHECKING:
    from .achievement import AchievementEntity
    from .attachment import AttachmentEntity
    from .comment import CommentEntity
    from .competence import CompetenceEntity
    from .level import LevelEntity
    from .project import ProjectEntity
    from .role import RoleEntity
    from .task import TaskEntity


class UserEntity(BaseEntityModel):
    """Доменная сущность Пользователя."""

    id: int
    first_name: str
    last_name: str | None
    patronymic: str | None
    telegram_id: int
    academic_points: int
    reputation_points: int
    join_date: date

    user_levels: list["LevelEntity"] = Field(default_factory=list)

    academic_role: Optional["RoleEntity"] = None
    admin_role: Optional["RoleEntity"] = None

    competencies: list["CompetenceEntity"] = Field(default_factory=list)
    achievements: list["AchievementEntity"] = Field(default_factory=list)

    created_tasks: list["TaskEntity"] = Field(default_factory=list)

    solutions: list["TaskEntity"] = Field(default_factory=list)
    comments: list["CommentEntity"] = Field(default_factory=list)
    attachments: list["AttachmentEntity"] = Field(default_factory=list)

    created_projects: list["ProjectEntity"] = Field(default_factory=list)
    projects: list["ProjectEntity"] = Field(default_factory=list)
