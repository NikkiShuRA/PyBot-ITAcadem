from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import BigInteger, DateTime, ForeignKey, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ...base_class import Base

if TYPE_CHECKING:
    from ..user_module import User
    from ..role_module import Role


class RoleEvent(Base):
    __tablename__ = "roles_events"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("users.id", ondelete="RESTRICT"), nullable=False)
    performed_by_user_id: Mapped[int | None] = mapped_column(BigInteger, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    roles_id_before: Mapped[int | None] = mapped_column(BigInteger, ForeignKey("roles.id", ondelete="SET NULL"), nullable=True)
    roles_id_after: Mapped[int | None] = mapped_column(BigInteger, ForeignKey("roles.id", ondelete="SET NULL"), nullable=True)
    reason: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())

    user: Mapped["User"] = relationship(
        foreign_keys=[user_id],
        back_populates="role_events",
        lazy="selectin"
    )
    performed_by: Mapped["User | None"] = relationship(
        foreign_keys=[performed_by_user_id],
        back_populates="performed_role_events",
        lazy="selectin"
    )
    role_before: Mapped["Role | None"] = relationship(
        foreign_keys=[roles_id_before],
        back_populates="role_events_before",
        lazy="selectin"
    )
    role_after: Mapped["Role | None"] = relationship(
        foreign_keys=[roles_id_after],
        back_populates="role_events_after",
        lazy="selectin"
    )
