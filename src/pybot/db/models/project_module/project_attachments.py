from __future__ import annotations

from sqlalchemy import BigInteger, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ...base_class import Base
from ..attachments import Attachment
from .projects import Project


class ProjectAttachment(Base):
    __tablename__ = "project_attachments"

    project_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("projects.id"), primary_key=True)
    attachments_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("attachments.id"), primary_key=True)

    project: Mapped[Project] = relationship(back_populates="attachments")
    attachment: Mapped[Attachment] = relationship(back_populates="project_attachments")
