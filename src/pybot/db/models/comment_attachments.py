from __future__ import annotations

from sqlalchemy import ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column

from ..base_class import Base


class CommentAttachment(Base):
    __tablename__ = "comment_attachments"

    comment_id: Mapped[int] = mapped_column(Integer, ForeignKey("comments.id"), primary_key=True)
    attachments_id: Mapped[int] = mapped_column(Integer, ForeignKey("attachments.id"), primary_key=True)
