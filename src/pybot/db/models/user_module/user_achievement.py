from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import BigInteger, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ...base_class import Base

if TYPE_CHECKING:
    from ..achievement import Achievement
    from .user import User


class UserAchievement(Base):
    __tablename__ = "user_achievements"

    user_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("users.id", ondelete="CASCADE"),
        primary_key=True,
    )
    achievements_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("achievements.id", ondelete="CASCADE"),
        primary_key=True,
    )

    user: Mapped[User] = relationship(
        "User",
        back_populates="achievements",
    )

    achievement: Mapped[Achievement] = relationship(
        "Achievement",
        back_populates="user_achievements",
    )
