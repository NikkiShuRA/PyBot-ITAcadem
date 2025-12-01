from __future__ import annotations

from sqlalchemy import BigInteger, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from ...base_class import Base


class TaskComment(Base):
    __tablename__ = "task_comments"

    task_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("tasks.id"), primary_key=True)
    comment_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("comments.id"), primary_key=True)
