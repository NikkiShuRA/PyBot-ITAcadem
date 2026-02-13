from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import Integer, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ...base_class import Base

if TYPE_CHECKING:
    from ..role_module import RoleEvent, RoleRequest, UserRole


class Role(Base):
    __tablename__ = "roles"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(Text, nullable=False, unique=True)
    description: Mapped[str | None] = mapped_column(Text)

    users: Mapped[list[UserRole]] = relationship("UserRole", back_populates="role")
    role_events: Mapped[list[RoleEvent]] = relationship(
        "RoleEvent",
        back_populates="role",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )
    role_requests: Mapped[list[RoleRequest]] = relationship("RoleRequest", back_populates="role")
