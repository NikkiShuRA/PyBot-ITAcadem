from __future__ import annotations

from sqlalchemy import BigInteger, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ...base_class import Base
from .projects import Project


class ProjectStatus(Base):
    __tablename__ = "projects_statuses"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(Text, nullable=False)
    description: Mapped[str] = mapped_column(Text)

    projects: Mapped[list[Project]] = relationship(back_populates="status")
