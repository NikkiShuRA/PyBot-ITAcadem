from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import BigInteger, DateTime, ForeignKey, Integer, Text, func, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ...base_class import Base

if TYPE_CHECKING:
    from ..user_module import User
    from . import Level, PointReasonType

class LevelEvent(Base):
    __tablename__ = "point_events"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("users.id", ondelete="RESTRICT"), nullable=False)
    performed_by_user_id: Mapped[int | None] = mapped_column(BigInteger, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    delta_points: Mapped[int] = mapped_column(Integer, nullable=False)
    points_before: Mapped[int] = mapped_column(Integer, nullable=False)
    points_after: Mapped[int] = mapped_column(Integer, nullable=False)
    level_id_before: Mapped[int | None] = mapped_column(BigInteger, ForeignKey("levels.id", ondelete="SET NULL"), nullable=True)
    level_id_after: Mapped[int | None] = mapped_column(BigInteger, ForeignKey("levels.id", ondelete="SET NULL"), nullable=True)
    reason_type_id: Mapped[int | None] = mapped_column(BigInteger, ForeignKey("point_reason_types.id", ondelete="SET NULL"),nullable=True)
    reason_text: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())

    user: Mapped["User"] = relationship(
        foreign_keys=[user_id],
        back_populates="points_events",
        lazy="selectin"
    )
    performed_by: Mapped["User | None"] = relationship(
        foreign_keys=[performed_by_user_id],
        back_populates="performed_points_events",
        lazy="selectin"
    )
    level_before: Mapped["Level | None"] = relationship(
        foreign_keys=[level_id_before],
        back_populates="points_events_before",
        lazy="selectin"
    )
    level_after: Mapped["Level | None"] = relationship(
        foreign_keys=[level_id_after],
        back_populates="points_events_after",
        lazy="selectin"
    )
    reason_type: Mapped["PointReasonType | None"] = relationship(
        foreign_keys=[reason_type_id],
        back_populates="points_events",
        lazy="selectin"
    )
