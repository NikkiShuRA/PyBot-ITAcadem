from datetime import date
from typing import TYPE_CHECKING

from pydantic import Field

from .base import BaseEntityModel

if TYPE_CHECKING:
    from .achievement import AchievementEntity
    from .attachment import AttachmentEntity
    from .comment import CommentEntity

from .user import UserEntity


class ProjectEntity(BaseEntityModel):  # TODO Добавить виды статусов для проекта
    """Доменная сущность Проекта."""

    id: int
    name: str
    description: str | None = None
    created_date: date
    author: "UserEntity"

    members: list["UserEntity"] = Field(default_factory=list)
    achievements: list["AchievementEntity"] = Field(default_factory=list)
    comments: list["CommentEntity"] = Field(default_factory=list)
    attachments: list["AttachmentEntity"] = Field(default_factory=list)
