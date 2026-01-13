from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import BigInteger, DateTime, ForeignKey, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ...base_class import Base

if TYPE_CHECKING:
    from ..user_module import User
    from ..task_module import TaskSolutionStatus, Task

class TaskSolution(Base):
    __tablename__ = "task_solutions"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    user_id: Mapped[int | None] = mapped_column(BigInteger, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    task_id: Mapped[int | None] = mapped_column(BigInteger, ForeignKey("tasks.id", ondelete="SET NULL"), nullable=True)
    solution_content: Mapped[str] = mapped_column(Text, nullable=False)
    status_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("task_solution_statuses.id", ondelete="RESTRICT"), nullable=False)
    created_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())

    user: Mapped["User | None"] = relationship(
        back_populates="task_solutions",
        lazy="selectin"
    )
    task: Mapped["Task | None"] = relationship(
        back_populates="solutions",
        lazy="selectin"
    )
    status: Mapped["TaskSolutionStatus"] = relationship(
        back_populates="solutions",
        lazy="selectin"
    )

