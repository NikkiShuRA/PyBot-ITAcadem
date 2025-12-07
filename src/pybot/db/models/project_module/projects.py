from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import BigInteger, Date, ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ...base_class import Base

if TYPE_CHECKING:
    from ..project_module import ProjectMember, ProjectStatus
    from ..user_module import User
    from .project_achievements import ProjectAchievement
    from .project_attachments import ProjectAttachment
    from .project_comments import ProjectComment


class Project(Base):
    __tablename__ = "projects"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(Text, nullable=False)
    description: Mapped[str] = mapped_column(Text)
    created_date: Mapped[str] = mapped_column(Date, nullable=False)
    status_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("projects_statuses.id"), nullable=False)
    user_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("users.id"), nullable=False)

    author: Mapped[User] = relationship("User", back_populates="created_projects")
    status: Mapped[ProjectStatus] = relationship("ProjectStatus", back_populates="projects")

    members: Mapped[list[ProjectMember]] = relationship(
        "ProjectMember", back_populates="project", cascade="all, delete-orphan"
    )

    achievements: Mapped[list[ProjectAchievement]] = relationship(
        "ProjectAchievement",
        foreign_keys="ProjectAchievement.project_id",
        back_populates="project",
        cascade="all, delete-orphan",
    )

    comments: Mapped[list[ProjectComment]] = relationship(
        "ProjectComment",
        back_populates="project",
        cascade="all, delete-orphan",
    )

    attachments: Mapped[list[ProjectAttachment]] = relationship(
        "ProjectAttachment",
        back_populates="project",
        cascade="all, delete-orphan",
    )
