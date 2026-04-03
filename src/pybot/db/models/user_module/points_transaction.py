from __future__ import annotations

from datetime import UTC, datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, Index, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ....core.constants import PointsTypeEnum
from ...base_class import Base

if TYPE_CHECKING:
    from .user import User


class PointsTransaction(Base):
    __tablename__ = "points_transactions"
    __table_args__ = (
        Index("ix_points_transactions_recipient_created_at", "recipient_id", "created_at"),
        Index("ix_points_transactions_points_type_created_at", "points_type", "created_at"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    recipient_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )
    giver_id: Mapped[int | None] = mapped_column(
        Integer,
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )
    amount: Mapped[int] = mapped_column(Integer, nullable=False)
    points_type: Mapped[PointsTypeEnum] = mapped_column(
        String(50),
        nullable=False,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=False),
        nullable=False,
        server_default=func.now(),
    )

    recipient: Mapped[User] = relationship(
        "User",
        foreign_keys=[recipient_id],
        back_populates="points_transactions_received",
    )
    giver: Mapped[User | None] = relationship(
        "User",
        foreign_keys=[giver_id],
        back_populates="points_transactions_given",
    )

    @classmethod
    def create(
        cls,
        *,
        recipient_id: int,
        giver_id: int | None,
        amount: int,
        points_type: PointsTypeEnum,
    ) -> PointsTransaction:
        return cls(
            recipient_id=recipient_id,
            giver_id=giver_id,
            amount=amount,
            points_type=points_type,
            created_at=datetime.now(UTC).replace(tzinfo=None),
        )
