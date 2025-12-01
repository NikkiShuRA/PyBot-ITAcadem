from __future__ import annotations

from sqlalchemy import BigInteger, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from ...base_class import Base


class TaskSolutionComment(Base):
    __tablename__ = "task_solution_comments"

    task_solutions_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("task_solutions.id"), primary_key=True)
    comment_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("comments.id"), primary_key=True)
