from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import BigInteger, ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ...base_class import Base

if TYPE_CHECKING:
    from ..attachment_module import AttachmentType
    from ..task_module import TaskAttachment, TaskSolutionAttachment, TaskSolution, Task

class Attachment(Base):
    __tablename__ = "attachments"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(Text, nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    type_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("attachment_types.id", ondelete="RESTRICT"), nullable=False)

    type: Mapped["AttachmentType"] = relationship(
        back_populates="attachments",
        lazy="selectin"
    )
    task_attachments: Mapped[list["TaskAttachment"]] = relationship(
        back_populates="attachment",
        cascade="all, delete-orphan",
        passive_deletes=True,
        lazy="selectin"
    )
    tasks: Mapped[list["Task"]] = relationship(
        secondary="task_attachments",
        back_populates="attachments",
        viewonly=True,
        lazy="selectin"
    )
    task_solution_attachments: Mapped[list["TaskSolutionAttachment"]] = relationship(
        back_populates="attachment",
        cascade="all, delete-orphan",
        passive_deletes=True,
        lazy="selectin"
    )
    task_solutions: Mapped[list["TaskSolution"]] = relationship(
        secondary="task_solutions_attachments",
        back_populates="attachments",
        viewonly=True,
        lazy="selectin"
    )
