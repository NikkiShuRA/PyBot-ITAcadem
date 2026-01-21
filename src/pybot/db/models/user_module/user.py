from __future__ import annotations

from datetime import date
from typing import TYPE_CHECKING

from sqlalchemy import BigInteger, Date, ForeignKey, Integer, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ...base_class import Base

if TYPE_CHECKING:
    from ..task_module import Task, TaskSolution
    from ..user_module import (
        AcademicRole,
        AdminRole,
        UserAchievement,
        UserActivityStatus,
        UserCompetence,
        UserLevel,
        Valuation,
    )


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    first_name: Mapped[str] = mapped_column(Text, nullable=False)
    last_name: Mapped[str | None] = mapped_column(Text)
    patronymic: Mapped[str | None] = mapped_column(Text)
    phone_number: Mapped[str | None] = mapped_column(Text)
    telegram_id: Mapped[int] = mapped_column(BigInteger, nullable=False, unique=True)
    github_url: Mapped[str | None] = mapped_column(Text)

    join_date: Mapped[date] = mapped_column(
        Date,
        nullable=False,
        server_default=func.current_date(),  # или func.now() с DateTime
    )
    activity_status_id: Mapped[int | None] = mapped_column(
        BigInteger,
        ForeignKey("user_activity_statuses.id"),
    )
    academic_points: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    reputation_points: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    academic_role_id: Mapped[int | None] = mapped_column(
        BigInteger,
        ForeignKey("academic_roles.id"),
    )
    admin_role_id: Mapped[int | None] = mapped_column(
        BigInteger,
        ForeignKey("admin_roles.id"),
    )

    activity_status: Mapped[UserActivityStatus | None] = relationship(
        "UserActivityStatus",
        back_populates="users",
    )

    user_levels: Mapped[list[UserLevel]] = relationship(
        "UserLevel",
        back_populates="user",
        foreign_keys="UserLevel.user_id",
        cascade="all, delete-orphan",
    )

    academic_role: Mapped[AcademicRole | None] = relationship(
        "AcademicRole",
        back_populates="users",
    )

    admin_role: Mapped[AdminRole | None] = relationship(
        "AdminRole",
        back_populates="users",
    )

    competencies: Mapped[list[UserCompetence]] = relationship(
        "UserCompetence",
        back_populates="user",
        cascade="all, delete-orphan",
        uselist=True,
    )

    achievements: Mapped[list[UserAchievement]] = relationship(
        "UserAchievement",
        back_populates="user",
        cascade="all, delete-orphan",
        uselist=True,
    )

    valuations_received: Mapped[list[Valuation]] = relationship(
        "Valuation",
        foreign_keys="Valuation.recipient_id",
        back_populates="recipient",
    )

    valuations_given: Mapped[list[Valuation]] = relationship(
        "Valuation",
        foreign_keys="Valuation.giver_id",
        back_populates="giver",
    )

    created_tasks: Mapped[list[Task]] = relationship("Task", back_populates="author")
    solutions: Mapped[list[TaskSolution]] = relationship("TaskSolution", back_populates="author")


    def __repr__(self) -> str:
        return f"User(id={self.id!r}, first_name={self.first_name!r}, last_name={self.last_name!r}, telegram_id={self.telegram_id!r}, academic_points={self.academic_points!r}, computation_points={self.reputation_points!r}, join_date={self.join_date!r})"  # noqa: E501
