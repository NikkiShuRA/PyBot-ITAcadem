from datetime import date
from typing import TYPE_CHECKING

from pydantic import Field

from .base import BaseEntityModel

if TYPE_CHECKING:
    from .comment import CommentEntity
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

    comments: list["CommentEntity"] = Field(default_factory=list)
