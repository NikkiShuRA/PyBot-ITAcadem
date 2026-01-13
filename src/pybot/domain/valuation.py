from datetime import date
from typing import TYPE_CHECKING

from ..core.constants import PointsTypeEnum
from .base import BaseEntityModel
from .user import UserEntity

if TYPE_CHECKING:
    from .user import UserEntity


class ValuationEntity(BaseEntityModel):
    """Доменная сущность Оценки."""

    id: int
    recipient: UserEntity
    giver: UserEntity
    reason: str | None
    points: int
    points_type: PointsTypeEnum
    created_at: date
