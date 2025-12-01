from __future__ import annotations

from sqlalchemy import BigInteger, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ...base_class import Base


class Competence(Base):
    __tablename__ = "competencies"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(Text, nullable=False)
    description: Mapped[str | None] = mapped_column(Text)

    user_competencies: Mapped[list[object]] = relationship(
        "UserCompetence",
        back_populates="competence",
        cascade="all, delete-orphan",
    )
