from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import BigInteger, Integer, Text
from sqlalchemy.dialects.postgresql import ENUM
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ....core.constants import PointsTypeEnum
from ...base_class import Base

if TYPE_CHECKING:
    from .user_level import UserLevel


class Level(Base):
    __tablename__ = "levels"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(Text, nullable=False)
    level_type: Mapped[PointsTypeEnum] = mapped_column(
        ENUM(PointsTypeEnum, name="points_type_enum", create_type=True), nullable=False
    )
    description: Mapped[str | None] = mapped_column(Text)
    required_points: Mapped[int] = mapped_column(Integer, nullable=False)

    user_levels: Mapped[UserLevel | None] = relationship(
        "UserLevel", back_populates="level", cascade="all, delete-orphan", foreign_keys="UserLevel.level_id"
    )
