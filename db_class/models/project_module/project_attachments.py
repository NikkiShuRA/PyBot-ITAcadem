from __future__ import annotations

from sqlalchemy import BigInteger, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from ...base_class import Base


class ProjectAttachment(Base):
    __tablename__ = "project_attachments"

    project_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("projects.id"), primary_key=True)
    attachments_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("attachments.id"), primary_key=True)
