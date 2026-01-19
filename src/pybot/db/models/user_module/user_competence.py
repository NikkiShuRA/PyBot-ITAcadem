from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import Boolean, ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ...base_class import Base

if TYPE_CHECKING:
    from .competence import Competence
    from .user import User


class UserCompetence(Base):
    __tablename__ = "user_competencies"

    user_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        primary_key=True,
    )

    competence_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("competencies.id", ondelete="CASCADE"),
        primary_key=True,
    )
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)

    user: Mapped[User] = relationship(
        "User",
        back_populates="competencies",
    )

    competence: Mapped[Competence] = relationship(
        "Competence",
        back_populates="user_competencies",
    )
