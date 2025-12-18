from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import BigInteger, ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ...base_class import Base

if TYPE_CHECKING:
    from ..task_module import Task
    from ..attachment_module import Attachment

class TaskAttachment(Base):
    __tablename__ = "task_attachments"
    __table_args__ = (UniqueConstraint("task_id", "attachments_id", name="uq_task_attachment"))

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    task_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("tasks.id", ondelete="CASCADE"), nullable=False)
    attachment_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("attachments.id", ondelete="CASCADE"), nullable=False)

    task: Mapped["Task"] = relationship(
        back_populates="task_attachments",
        lazy="selectin"
    )
    attachment: Mapped["Attachment"] = relationship(
        back_populates="task_attachments",
        lazy="selectin"
    )
