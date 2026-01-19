from __future__ import annotations

from datetime import datetime

from sqlalchemy import BigInteger, DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ....core.constants import PointsTypeEnum
from ...base_class import Base
from .user import User


class Valuation(Base):
    __tablename__ = "valuations"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    recipient_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )
    giver_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )
    reason: Mapped[str | None] = mapped_column(Text)
    points: Mapped[int] = mapped_column(Integer, nullable=False)
    points_type: Mapped[PointsTypeEnum] = mapped_column(
        String(50),
        nullable=False,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=False),  # SQLite не поддерживает timezone
        nullable=False,
        server_default=func.now(),
    )
    recipient: Mapped[User] = relationship(
        "User",
        foreign_keys=[recipient_id],
        back_populates="valuations_received",
    )
    giver: Mapped[User] = relationship(
        "User",
        foreign_keys=[giver_id],
        back_populates="valuations_given",
    )
