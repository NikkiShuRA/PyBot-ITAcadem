from __future__ import annotations

from sqlalchemy import BigInteger, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from ...base_class import Base


class ProjectAchievement(Base):
    __tablename__ = "project_achievements"

    project_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("projects.id"), primary_key=True)

    achievements_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("achievements.id"), primary_key=True)
