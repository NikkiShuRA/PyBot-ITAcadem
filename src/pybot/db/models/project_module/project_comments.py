from __future__ import annotations

from sqlalchemy import BigInteger, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ...base_class import Base
from ..comments import Comment
from .projects import Project


class ProjectComment(Base):
    __tablename__ = "project_comments"

    project_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("projects.id"), primary_key=True)
    comment_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("comments.id"), primary_key=True)

    project: Mapped[Project] = relationship(back_populates="comments")
    comment: Mapped[Comment] = relationship(back_populates="project_comments")
