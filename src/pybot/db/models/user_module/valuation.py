from __future__ import annotations

from sqlalchemy import BigInteger, ForeignKey, Integer, Text
from sqlalchemy.dialects.postgresql import ENUM
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ....core.constants import PointsTypeEnum
from ...base_class import Base
from .user import User


class Valuation(Base):
    __tablename__ = "valuation"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
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
        ENUM(PointsTypeEnum, name="points_type_enum", create_type=True), nullable=False
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
