from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, Enum, ForeignKey, Index, Integer, func, text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ....core.constants import RequestStatus
from ...base_class import Base

if TYPE_CHECKING:
    from ..role_module import Role
    from ..user_module import User


class RoleRequest(Base):
    __tablename__ = "role_requests"
    __table_args__ = (
        Index(
            "uq_role_requests_pending_by_user",
            "user_id",
            unique=True,
            sqlite_where=text("status = 'PENDING'"),
            postgresql_where=text("status = 'PENDING'"),
        ),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False)
    role_id: Mapped[int] = mapped_column(Integer, ForeignKey("roles.id"), nullable=False)
    status: Mapped[RequestStatus] = mapped_column(
        Enum(
            RequestStatus,
            name="request_status_enum",
            native_enum=False,
            validate_strings=True,
            create_constraint=True,
        ),
        default=RequestStatus.PENDING,
        nullable=False,
    )
    created_at: Mapped[datetime] = mapped_column(DateTime(), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(), server_default=func.now(), onupdate=func.now(), nullable=False
    )
    user: Mapped[User] = relationship("User", back_populates="role_requests")
    role: Mapped[Role] = relationship("Role", back_populates="role_requests")

    def change_status(self, status: RequestStatus) -> None:
        self.status = status
