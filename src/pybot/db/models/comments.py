from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import TIMESTAMP, ForeignKey, Integer, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..base_class import Base

if TYPE_CHECKING:
    from .project_module.project_comments import ProjectComment
    from .task_module.task_comments import TaskComment
    from .task_module.task_solution_comments import TaskSolutionComment
    from .user_module.user import User


class Comment(Base):
    __tablename__ = "comments"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    datetime: Mapped[str] = mapped_column(TIMESTAMP, nullable=False)

    author: Mapped[User] = relationship(back_populates="comments")

    task_solution_comments: Mapped[list[TaskSolutionComment]] = relationship(
        "TaskSolutionComment",
        back_populates="comment",
        cascade="all, delete-orphan",
    )

    task_comments: Mapped[list[TaskComment]] = relationship(
        "TaskComment",
        back_populates="comment",
        cascade="all, delete-orphan",
    )

    project_comments: Mapped[list[ProjectComment]] = relationship(
        "ProjectComment",
        back_populates="comment",
        cascade="all, delete-orphan",
    )
