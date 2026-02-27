from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, Integer, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ...base_class import Base

if TYPE_CHECKING:
    from .level import Level
    from .user import User


class UserLevel(Base):
    __tablename__ = "user_levels"
    __table_args__ = (UniqueConstraint("user_id", "level_id", name="uq_user_level"),)

    id: Mapped[int] = mapped_column(Integer, autoincrement=True, primary_key=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False)
    level_id: Mapped[int] = mapped_column(Integer, ForeignKey("levels.id"), nullable=False)

    user: Mapped[User] = relationship("User", back_populates="user_levels")
    level: Mapped[Level] = relationship("Level", back_populates="user_levels")
