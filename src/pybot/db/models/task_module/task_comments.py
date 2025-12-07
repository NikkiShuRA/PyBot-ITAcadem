from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import BigInteger, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ...base_class import Base

if TYPE_CHECKING:
    from ..comments import Comment
    from .tasks import Task


class TaskComment(Base):
    __tablename__ = "task_comments"

    task_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("tasks.id"), primary_key=True)
    comment_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("comments.id"), primary_key=True)

    task: Mapped[Task] = relationship("Task", back_populates="comments")
    comment: Mapped[Comment] = relationship("Comment", back_populates="task_comments")
