from __future__ import annotations

from sqlalchemy import BigInteger, ForeignKey, Integer, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ...base_class import Base


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

    recipient: Mapped[object] = relationship(
        "User",
        foreign_keys=[recipient_id],
        back_populates="valuations_received",
    )
    giver: Mapped[object] = relationship(
        "User",
        foreign_keys=[giver_id],
        back_populates="valuations_given",
    )
