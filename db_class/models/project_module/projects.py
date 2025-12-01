from __future__ import annotations

from sqlalchemy import BigInteger, Date, ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column

from ...base_class import Base


class Project(Base):
    __tablename__ = "projects"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(Text, nullable=False)
    description: Mapped[str] = mapped_column(Text)
    created_date: Mapped[str] = mapped_column(Date, nullable=False)
    status_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("projects_statuses.id"), nullable=False)
    user_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
