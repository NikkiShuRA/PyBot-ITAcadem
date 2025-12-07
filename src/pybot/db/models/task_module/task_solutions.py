from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import BigInteger, Date, ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ...base_class import Base

if TYPE_CHECKING:
    from ..user_module import User
    from .task_solution_comments import TaskSolutionComment
    from .task_solution_statuses import TaskSolutionStatus
    from .tasks import Task


class TaskSolution(Base):
    __tablename__ = "task_solutions"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    task_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("tasks.id"), nullable=False)
    user_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("users.id"), nullable=False)
    status_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("task_solution_statuses.id"), nullable=False)
    content: Mapped[str] = mapped_column(Text)
    solution_url: Mapped[str] = mapped_column(Text)
    created_date: Mapped[str] = mapped_column(Date, nullable=False)

    task: Mapped[Task] = relationship("Task", back_populates="solutions")
    author: Mapped[User] = relationship("User", back_populates="solutions")
    status: Mapped[TaskSolutionStatus] = relationship("TaskSolutionStatus", back_populates="solutions")

    comments: Mapped[list[TaskSolutionComment]] = relationship(
        "TaskSolutionComment",
        back_populates="task",
        cascade="all, delete-orphan",
    )
