from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import BigInteger, ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ...base_class import Base

if TYPE_CHECKING:
    from ..role_module import Role, Permission
    
class RolePermission (Base):
    __tablename__ = "role_permissions"
    __table_args__ = (UniqueConstraint("role_id", "permission_id", name="uq_role_permission"),)
    
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    role_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("roles.id", ondelete="CASCADE"), nullable=False)
    permission_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("permissions.id", ondelete="CASCADE"), nullable=False)

    role: Mapped["Role"] = relationship(
        back_populates="role_permissions"
    )
    permission: Mapped["Permission"] = relationship(
        back_populates="role_permissions"
    )