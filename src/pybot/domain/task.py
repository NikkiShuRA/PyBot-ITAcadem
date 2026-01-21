from datetime import date
from typing import TYPE_CHECKING

from .base import BaseEntityModel

if TYPE_CHECKING:
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
