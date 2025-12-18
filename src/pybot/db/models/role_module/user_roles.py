from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import BigInteger, ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ...base_class import Base

if TYPE_CHECKING:
    from ..role_module import Role, RoleSystem
    from ..user_module import User


class UserRole(Base):
    __tablename__ = "user_roles"
    __table_args__ = (UniqueConstraint("user_id", "role_system_id", name="uq_user_role_systems"))

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    role_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("roles.id", ondelete="CASCADE"), nullable=False)
    role_system_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("role_systems.id", ondelete="CASCADE"), nullable=False)

    user: Mapped["User"] = relationship(
        back_populates="user_roles",
        lazy="selectin"
    )
    role: Mapped["Role"] = relationship(
        back_populates="user_roles",
        lazy="selectin"
    )
    role_system: Mapped["RoleSystem"] = relationship(
        back_populates="user_roles",
        lazy="selectin"
    )
