from __future__ import annotations

from sqlalchemy import BigInteger, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ...base_class import Base
from .task_solutions import TaskSolution


class TaskSolutionStatus(Base):
    __tablename__ = "task_solution_statuses"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(Text, nullable=False)
    description: Mapped[str] = mapped_column(Text)

    solutions: Mapped[list[TaskSolution]] = relationship("TaskSolution", back_populates="status")
