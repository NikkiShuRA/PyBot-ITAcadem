from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, Integer, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..base_class import Base

if TYPE_CHECKING:
    from .project_module.project_attachments import ProjectAttachment
    from .task_module.task_attachments import TaskAttachment


class Attachment(Base):
    __tablename__ = "attachments"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(Text, nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    type_id: Mapped[int] = mapped_column(Integer, ForeignKey("attachments_types.id"), nullable=False)

    task_attachments: Mapped[list[TaskAttachment]] = relationship(
        "TaskAttachment",
        back_populates="attachment",
        cascade="all, delete-orphan",
    )

    project_attachments: Mapped[list[ProjectAttachment]] = relationship(
        "ProjectAttachment",
        back_populates="attachment",
        cascade="all, delete-orphan",
    )
