from datetime import date
from typing import TYPE_CHECKING

from .base import BaseEntityModel

if TYPE_CHECKING:
    from ..domain import UserEntity, LevelSystemEntity, LevelEventReasonTypeEntity


class LevelEventEntity(BaseEntityModel):
    """Доменная сущность Оценки."""

    id: int
    recipient: UserEntity   
    giver: UserEntity
    reason_type: LevelEventReasonTypeEntity
    reason: str | None
    points: int
    level_system_type: LevelSystemEntity
    created_at: date
