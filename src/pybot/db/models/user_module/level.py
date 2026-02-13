from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import Integer, String, Text
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ....core.constants import LevelTypeEnum
from ....dto.value_objects import Points
from ...base_class import Base

if TYPE_CHECKING:
    from .user_level import UserLevel


class Level(Base):
    __tablename__ = "levels"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(Text, nullable=False)
    level_type: Mapped[LevelTypeEnum] = mapped_column(
        String(50),
        nullable=False,
    )
    description: Mapped[str | None] = mapped_column(Text)
    required_points: Mapped[int] = mapped_column(Integer, nullable=False)

    user_levels: Mapped[UserLevel | None] = relationship(
        "UserLevel", back_populates="level", cascade="all, delete-orphan", foreign_keys="UserLevel.level_id"
    )

    @hybrid_property
    def threshold_vo(self) -> Points:
        return Points(value=self.required_points, point_type=self.level_type)

    @threshold_vo.expression  # ty:ignore[invalid-argument-type]
    def threshold_vo(cls) -> int:  # noqa: N805
        return cls.required_points
