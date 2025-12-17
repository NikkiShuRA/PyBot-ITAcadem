from datetime import date
from typing import TYPE_CHECKING

from .base import BaseEntityModel

if TYPE_CHECKING:
    from .user import UserEntity


class CommentEntity(BaseEntityModel):
    """Доменная сущность Комментария."""

    id: int
    text: str
    datetime: date
    author: "UserEntity"
