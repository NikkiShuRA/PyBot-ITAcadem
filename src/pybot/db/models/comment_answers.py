from __future__ import annotations

from sqlalchemy import ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column

from ..base_class import Base


class CommentAnswer(Base):
    __tablename__ = "comment_answers"

    comment_id: Mapped[int] = mapped_column(Integer, ForeignKey("comments.id"), primary_key=True)
    answer_id: Mapped[int] = mapped_column(Integer, ForeignKey("comments.id"), primary_key=True)
