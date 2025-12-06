from __future__ import annotations

from datetime import date

from sqlalchemy import BigInteger, Date, ForeignKey, Integer, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ...base_class import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
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
    level_id: Mapped[int | None] = mapped_column(
        BigInteger,
        ForeignKey("levels.id"),
    )
    academic_role_id: Mapped[int | None] = mapped_column(
        BigInteger,
        ForeignKey("academic_roles.id"),
    )
    admin_role_id: Mapped[int | None] = mapped_column(
        BigInteger,
        ForeignKey("admin_roles.id"),
    )

    activity_status: Mapped[object | None] = relationship(
        "UserActivityStatus",
        back_populates="users",
    )
    level: Mapped[object | None] = relationship(
        "Level",
        back_populates="users",
    )
    academic_role: Mapped[object | None] = relationship(
        "AcademicRole",
        back_populates="users",
    )
    admin_role: Mapped[object | None] = relationship(
        "AdminRole",
        back_populates="users",
    )

    competencies: Mapped[list[object]] = relationship(
        "UserCompetence",
        back_populates="user",
        cascade="all, delete-orphan",
    )
    achievements: Mapped[list[object]] = relationship(
        "UserAchievement",
        back_populates="user",
        cascade="all, delete-orphan",
    )
    valuations_received: Mapped[list[object]] = relationship(
        "Valuation",
        foreign_keys="Valuation.recipient_id",
        back_populates="recipient",
    )
    valuations_given: Mapped[list[object]] = relationship(
        "Valuation",
        foreign_keys="Valuation.giver_id",
        back_populates="giver",
    )
