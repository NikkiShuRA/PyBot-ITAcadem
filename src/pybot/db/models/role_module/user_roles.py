from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import BigInteger, Date, ForeignKey, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ...base_class import Base

if TYPE_CHECKING:
    from ..user_module import User
    
class UserRoles (Base):
    __tablename__ = "user_roles"
    __table_args__ = (UniqueConstraint("user_id", "type_role_system_id", name="uq_user_type_role_system"))
    
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    role_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("roles.id", ondelete="CASCADE"), nullable=False)
