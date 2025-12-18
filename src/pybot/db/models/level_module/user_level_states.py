from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import BigInteger, ForeignKey, Integer, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ...base_class import Base

if TYPE_CHECKING:
    from ..user_module import User
    from ..level_module import Level

class UserLevelState(Base):
    __tablename__ = "user_level_states"
    __table_args__ = (UniqueConstraint("user_id", "level_system_id", name="uq_user_level_state_user"))

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    points: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    level_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("levels.id", ondelete="RESTRICT"), nullable=False)
    level_system_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("level_systems.id", ondelete="CASCADE"), nullable=False)

    user: Mapped["User"] = relationship(
        back_populates="level_state",
        lazy="selectin"
    )
    level: Mapped["Level"] = relationship(
        back_populates="users_states",
        lazy="selectin"
    )
