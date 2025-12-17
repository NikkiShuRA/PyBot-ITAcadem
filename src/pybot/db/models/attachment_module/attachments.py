from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import BigInteger, ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ...base_class import Base

if TYPE_CHECKING:
    from .attachment_types import AttachmentTypes

class Attachment(Base):
    __tablename__ = "attachments"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(Text, nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    type_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("attachment_types.id", ondelete="CASCADE"), nullable=False)

    attachment_type: Mapped["AttachmentTypes"] = relationship(back_populates="attachments")
