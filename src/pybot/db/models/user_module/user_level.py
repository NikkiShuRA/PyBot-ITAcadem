from sqlalchemy import ForeignKey, Integer, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ...base_class import Base
from . import Level, User


class UserLevel(Base):
    __tablename__ = "user_levels"

    id: Mapped[int] = mapped_column(Integer, autoincrement=True, primary_key=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False)
    level_id: Mapped[int] = mapped_column(Integer, ForeignKey("levels.id"), nullable=False)

    __table_args__ = (UniqueConstraint("user_id", "level_id", name="uq_user_level"),)

    user: Mapped[User] = relationship("User", back_populates="user_levels")
    level: Mapped[Level] = relationship("Level", back_populates="user_levels")
