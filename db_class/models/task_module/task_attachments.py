from __future__ import annotations

from sqlalchemy import BigInteger, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from ...base_class import Base


class TaskAttachment(Base):
    __tablename__ = "task_attachments"

    task_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("tasks.id"), primary_key=True)
    attachments_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("attachments.id"), primary_key=True)
