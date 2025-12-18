from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import BigInteger, ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ...base_class import Base

if TYPE_CHECKING:
    from ..role_module import RoleSystem, Permission, RolePermission, UserRole, RoleEvent
    from ..user_module import User


class Role(Base):
    __tablename__ = "roles"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(Text, nullable=False, unique=True)
    description: Mapped[str | None] = mapped_column(Text)
    role_system_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("role_systems.id", ondelete="CASCADE"), nullable=False)

    system: Mapped["RoleSystem"] = relationship(
        back_populates="roles",
        lazy="selectin"
    )
    role_permissions: Mapped[list["RolePermission"]] = relationship(
        back_populates="role",
        cascade="all, delete-orphan",
        passive_deletes=True,
        lazy="selectin"
    )
    permissions: Mapped[list["Permission"]] = relationship(
        secondary="role_permissions",
        back_populates="roles",
        viewonly=True,
        lazy="selectin"
    )
    user_roles: Mapped[list["UserRole"]] = relationship(
        back_populates="role",
        cascade="all, delete-orphan",
        passive_deletes=True,
        lazy="selectin"
    )
    users: Mapped[list["User"]] = relationship(
        secondary="user_roles",
        back_populates="roles",
        viewonly=True,
        lazy="selectin"
    )
    role_events_before: Mapped[list["RoleEvent"]] = relationship(
        back_populates="role_before",
        foreign_keys="RoleEvent.roles_id_before",
        passive_deletes=True,
        lazy="selectin"
    )
    role_events_after: Mapped[list["RoleEvent"]] = relationship(
        back_populates="role_after",
        foreign_keys="RoleEvent.roles_id_after",
        passive_deletes=True,
        lazy="selectin"
    )
