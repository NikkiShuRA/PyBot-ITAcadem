from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import BigInteger, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ...base_class import Base

if TYPE_CHECKING:
    from ..user_module import UserActivity
    from ..role_module import UserRole, Role, RoleEvent
    from ..level_module import UserLevelState, PointEvent
    from ..task_module import Task, TaskSolution


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(Text, nullable=False)
    surname: Mapped[str] = mapped_column(Text, nullable=False)
    patronymic: Mapped[str | None] = mapped_column(Text)
    telegram_id: Mapped[int] = mapped_column(BigInteger, nullable=False, unique=True)

    activity: Mapped["UserActivity"] = relationship(
        back_populates="user",
        uselist=False,
        cascade="all, delete-orphan",
        passive_deletes=True,
        lazy="selectin"
    )
    user_roles: Mapped[list["UserRole"]] = relationship(
        back_populates="user",
        cascade="all, delete-orphan",
        passive_deletes=True,
        lazy="selectin"
    )
    roles: Mapped[list["Role"]] = relationship(
        secondary="user_roles",
        back_populates="users",
        viewonly=True,
        lazy="selectin"
    )
    role_events: Mapped[list["RoleEvent"]] = relationship(
        back_populates="user",
        foreign_keys="RoleEvent.user_id",
        passive_deletes=True,
        lazy="selectin"
    )
    performed_role_events: Mapped[list["RoleEvent"]] = relationship(
        back_populates="performed_by",
        foreign_keys="RoleEvent.performed_by_user_id",
        passive_deletes=True,
        lazy="selectin"
    )
    level_state: Mapped["UserLevelState | None"] = relationship(
        back_populates="user",
        uselist=False,
        cascade="all, delete-orphan",
        passive_deletes=True,
        lazy="selectin"
    )
    points_events: Mapped[list["PointEvent"]] = relationship(
        back_populates="user",
        foreign_keys="PointEvent.user_id",
        passive_deletes=True,
        lazy="selectin"
    )
    performed_points_events: Mapped[list["PointEvent"]] = relationship(
        back_populates="performed_by",
        foreign_keys="PointEvent.performed_by_user_id",
        passive_deletes=True,
        lazy="selectin"
    )
    created_tasks: Mapped[list["Task"]] = relationship(
        back_populates="creator",
        passive_deletes=True,
        lazy="selectin"
    )
    task_solutions: Mapped[list["TaskSolution"]] = relationship(
        back_populates="user",
        passive_deletes=True,
        lazy="selectin"
    )

