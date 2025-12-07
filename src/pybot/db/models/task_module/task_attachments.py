from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import BigInteger, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ...base_class import Base

if TYPE_CHECKING:
    from ..attachments import Attachment
    from .tasks import Task


class TaskAttachment(Base):
    __tablename__ = "task_attachments"

    task_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("tasks.id"), primary_key=True)
    attachments_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("attachments.id"), primary_key=True)

    task: Mapped[Task] = relationship("Task", back_populates="attachments")
    attachment: Mapped[Attachment] = relationship("Attachment", back_populates="task_attachments")
