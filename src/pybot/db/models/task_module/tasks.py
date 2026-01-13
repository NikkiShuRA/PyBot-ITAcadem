from __future__ import annotations

from datetime import date, datetime
from typing import TYPE_CHECKING

from sqlalchemy import BigInteger, Boolean, Date, DateTime, ForeignKey, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ...base_class import Base

if TYPE_CHECKING:
    from ..user_module import User
    from ..task_module import TaskSolution

class Task(Base):
    __tablename__ = "tasks"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(Text, nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    user_id: Mapped[int | None] = mapped_column(BigInteger, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    tasks_content: Mapped[str] = mapped_column(Text, nullable=False)
    created_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    due_date: Mapped[date | None] = mapped_column(Date)

    creator: Mapped["User | None"] = relationship(
        back_populates="created_tasks",
        lazy="selectin"
    )
    solutions: Mapped[list["TaskSolution"]] = relationship(
        back_populates="task",
        passive_deletes=True,
        lazy="selectin"
    )
