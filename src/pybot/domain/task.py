from datetime import date
from typing import TYPE_CHECKING

from pydantic import Field

from .base import BaseEntityModel

if TYPE_CHECKING:
    from .attachment import AttachmentEntity
    from .competence import CompetenceEntity
    from .user import UserEntity


class TaskEntity(BaseEntityModel):
    """Доменная сущность Задачи."""

    id: int
    name: str
    description: str
    created_date: date
    is_active: bool
    due_date: date
    author: "UserEntity"

    comments: list["CompetenceEntity"] = Field(default_factory=list)
    attachments: list["AttachmentEntity"] = Field(default_factory=list)


# TaskEntity.model_rebuild()
