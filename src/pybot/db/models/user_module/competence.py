from __future__ import annotations

from sqlalchemy import Integer, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ...base_class import Base
from ..user_module.user_competence import UserCompetence


class Competence(Base):
    __tablename__ = "competencies"
    __table_args__ = (UniqueConstraint("name", name="uq_competencies_name"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(Text, nullable=False)
    description: Mapped[str | None] = mapped_column(Text)

    user_competencies: Mapped[list[UserCompetence]] = relationship(
        "UserCompetence",
        back_populates="competence",
        cascade="all, delete-orphan",
    )
