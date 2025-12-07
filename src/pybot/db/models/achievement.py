from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import BigInteger, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..base_class import Base

if TYPE_CHECKING:
    from .project_module.project_achievements import ProjectAchievement
    from .user_module.user_achievement import UserAchievement


class Achievement(Base):
    __tablename__ = "achievements"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(Text, nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    icon_url: Mapped[str | None] = mapped_column(Text)

    user_achievements: Mapped[list[UserAchievement]] = relationship(
        "UserAchievement",
        back_populates="achievement",
        cascade="all, delete-orphan",
    )

    project_achievements: Mapped[list[ProjectAchievement]] = relationship(
        "ProjectAchievement",
        foreign_keys="ProjectAchievement.achievements_id",
        back_populates="achievement",
        cascade="all, delete-orphan",
    )
