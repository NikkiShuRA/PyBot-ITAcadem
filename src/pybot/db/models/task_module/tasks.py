from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import BigInteger, Boolean, Date, ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ...base_class import Base

if TYPE_CHECKING:
    from ..task_module import TaskAttachment, TaskComment, TaskSolution
    from ..user_module import User


class Task(Base):
    __tablename__ = "tasks"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(Text, nullable=False)
    description: Mapped[str] = mapped_column(Text)
    created_date: Mapped[str] = mapped_column(Date, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    due_date: Mapped[str] = mapped_column(Date)
    user_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("users.id"), nullable=False)

    author: Mapped[User] = relationship("User", back_populates="created_tasks")

    solutions: Mapped[list[TaskSolution]] = relationship(
        "TaskSolution", back_populates="task", cascade="all, delete-orphan"
    )

    # Связь через ассоциативную таблицу TaskComment
    comments: Mapped[list[TaskComment]] = relationship(
        "TaskComment", back_populates="task", cascade="all, delete-orphan"
    )

    # Связь через ассоциативную таблицу TaskAttachment
    attachments: Mapped[list[TaskAttachment]] = relationship(
        "TaskAttachment", back_populates="task", cascade="all, delete-orphan"
    )
