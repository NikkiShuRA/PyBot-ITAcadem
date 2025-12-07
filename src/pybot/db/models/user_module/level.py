from __future__ import annotations

from sqlalchemy import BigInteger, Integer, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ...base_class import Base
from .user import User


class Level(Base):
    __tablename__ = "levels"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(Text, nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    required_points: Mapped[int] = mapped_column(Integer, nullable=False)

    users: Mapped[list[User]] = relationship(
        "User",
        back_populates="level",
    )
