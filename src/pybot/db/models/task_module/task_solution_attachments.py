from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import BigInteger, ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ...base_class import Base

if TYPE_CHECKING:
    from ..task_module import TaskSolution
    from ..attachment_module import Attachment

class TaskSolutionAttachment(Base):
    __tablename__ = "task_solutions_attachments"
    __table_args__ = (UniqueConstraint("task_solution_id", "attachments_id", name="uq_task_solution_attachment"))

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    task_solution_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("task_solutions.id", ondelete="CASCADE"), nullable=False)
    attachment_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("attachments.id", ondelete="CASCADE"), nullable=False)

    solution: Mapped["TaskSolution"] = relationship(
        back_populates="solution_attachments",
        lazy="selectin"
    )
    attachment: Mapped["Attachment"] = relationship(
        back_populates="task_solution_attachments",
        lazy="selectin"
    )
