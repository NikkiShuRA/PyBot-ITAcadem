from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import BigInteger, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ...base_class import Base

if TYPE_CHECKING:
    from ..attachment_module import Attachment
    from ..task_module import TaskSolution

class TaskSolutionAttachment(Base):
    __tablename__ = "task_solution_attachments"

    task_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("tasks_solution.id"), primary_key=True)
    attachments_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("attachments.id"), primary_key=True)

    task: Mapped["TaskSolution"] = relationship(back_populates="attachments")
    attachment: Mapped["Attachment"] = relationship("Attachment", back_populates="task_attachments")