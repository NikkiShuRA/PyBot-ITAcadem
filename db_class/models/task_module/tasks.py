from __future__ import annotations

from sqlalchemy import BigInteger, Boolean, Date, Text
from sqlalchemy.orm import Mapped, mapped_column

from ...base_class import Base


class Task(Base):
    __tablename__ = "tasks"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(Text, nullable=False)
    description: Mapped[str] = mapped_column(Text)
    created_date: Mapped[str] = mapped_column(Date, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    due_date: Mapped[str] = mapped_column(Date)
    user_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
