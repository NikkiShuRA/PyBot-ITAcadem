from __future__ import annotations

from sqlalchemy import BigInteger, Date, ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column

from ...base_class import Base


class TaskSolution(Base):
    __tablename__ = "task_solutions"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    task_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("tasks.id"), nullable=False)
    user_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    status_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("task_solution_statuses.id"), nullable=False)
    content: Mapped[str] = mapped_column(Text)
    solution_url: Mapped[str] = mapped_column(Text)
    created_date: Mapped[str] = mapped_column(Date, nullable=False)
