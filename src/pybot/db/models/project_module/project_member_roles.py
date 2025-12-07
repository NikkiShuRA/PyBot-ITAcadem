from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import BigInteger, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ...base_class import Base

if TYPE_CHECKING:
    from .project_members import ProjectMember


class ProjectMemberRole(Base):
    __tablename__ = "project_member_roles"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(Text, nullable=False)
    description: Mapped[str] = mapped_column(Text)

    members: Mapped[list[ProjectMember]] = relationship(back_populates="role")
