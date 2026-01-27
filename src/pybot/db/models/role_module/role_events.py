from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, Enum, ForeignKey, Integer, Text, text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ....core.constants import RoleEventOperandEnum
from ...base_class import Base

if TYPE_CHECKING:
    from ..role_module import Role
    from ..user_module import User


class RoleEvent(Base):
    __tablename__ = "role_events"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    to_user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    from_user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    operand: Mapped[RoleEventOperandEnum] = mapped_column(
        Enum(
            RoleEventOperandEnum,
            name="role_event_operand_enum",
            native_enum=False,
            validate_strings=True,
            create_constraint=True,
        ),
        nullable=False,
    )
    role_id: Mapped[int] = mapped_column(Integer, ForeignKey("roles.id", ondelete="CASCADE"), nullable=False)
    reason: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(), server_default=text("CURRENT_TIMESTAMP"), nullable=False)

    to_user: Mapped[User] = relationship("User", foreign_keys=[to_user_id], back_populates="role_events_to")
    from_user: Mapped[User] = relationship("User", foreign_keys=[from_user_id], back_populates="role_events_from")
    role: Mapped[Role] = relationship("Role", back_populates="role_events")
