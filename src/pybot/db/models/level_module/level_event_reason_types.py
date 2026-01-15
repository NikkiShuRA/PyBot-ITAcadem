from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import BigInteger, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ...base_class import Base

if TYPE_CHECKING:
    from . import LevelEvent

class LevelEventReasonType(Base):
    __tablename__ = "point_reason_types"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(Text, nullable=False, unique=True)
    description: Mapped[str | None] = mapped_column(Text)

    points_events: Mapped[list["LevelEvent"]] = relationship(
        back_populates="reason_type",
        passive_deletes=True,
        lazy="selectin"
    )
