from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import BigInteger, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ...base_class import Base

if TYPE_CHECKING:
    from ..attachment_module import Attachment

class AttachmentTypes(Base):
    __tablename__ = "attachment_types"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(Text, nullable=False, unique=True)
    description: Mapped[str] = mapped_column(Text)

    attachments: Mapped[list["Attachment"]] = relationship(
        back_populates="attachment_type",
        cascade="all, delete-orphan", 
        passive_deletes=True, 
    )
