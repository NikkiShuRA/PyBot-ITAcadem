from __future__ import annotations

from sqlalchemy import BigInteger, Boolean
from sqlalchemy.orm import Mapped, mapped_column

from ...base_class import Base


class UserTask(Base):
    __tablename__ = "user_tasks"

    user_id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    task_id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    completion_status: Mapped[bool] = mapped_column(Boolean, nullable=False)
