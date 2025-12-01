from __future__ import annotations

from sqlalchemy import TIMESTAMP, BigInteger, Text
from sqlalchemy.orm import Mapped, mapped_column

from ..base_class import Base


class Comment(Base):
    __tablename__ = "comments"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    datetime: Mapped[str] = mapped_column(TIMESTAMP, nullable=False)
