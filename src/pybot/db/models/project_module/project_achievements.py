from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import BigInteger, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ...base_class import Base

if TYPE_CHECKING:
    from ..achievement import Achievement
    from .projects import Project


class ProjectAchievement(Base):
    __tablename__ = "project_achievements"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    project_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("projects.id"))

    achievements_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("achievements.id"))

    project: Mapped[Project] = relationship(back_populates="achievements")
    achievement: Mapped[Achievement] = relationship(back_populates="project_achievements")
