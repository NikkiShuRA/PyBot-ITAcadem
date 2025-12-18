from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import BigInteger, ForeignKey, Integer, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ...base_class import Base

if TYPE_CHECKING:
    from ..level_module import LevelSystem, UserLevelState, PointEvent

class Level(Base):
    __tablename__ = "levels"
    __table_args__ = (UniqueConstraint("type_level_system_id", "name", name="uq_levels_system_name"))

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    level_system_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("level_systems.id", ondelete="CASCADE"),nullable=False)
    name: Mapped[str] = mapped_column(Text, nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    required_points: Mapped[int] = mapped_column(Integer, nullable=False)

    system: Mapped["LevelSystem"] = relationship(
        back_populates="levels",
        lazy="selectin"
    )
    users_states: Mapped[list["UserLevelState"]] = relationship(
        back_populates="level",
        passive_deletes=True,
        lazy="selectin"
    )
    points_events_before: Mapped[list["PointEvent"]] = relationship(
        back_populates="level_before",
        foreign_keys="PointEvent.level_id_before",
        passive_deletes=True,
        lazy="selectin"
    )
    points_events_after: Mapped[list["PointEvent"]] = relationship(
        back_populates="level_after",
        foreign_keys="PointEvent.level_id_after",
        passive_deletes=True,
        lazy="selectin"
    )
