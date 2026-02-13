from __future__ import annotations

from collections.abc import Sequence
from datetime import UTC, date, datetime, timedelta
from typing import TYPE_CHECKING

from sqlalchemy import BigInteger, Date, DateTime, ForeignKey, Integer, Text, func
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ....core.constants import LevelTypeEnum
from ....domain.exceptions import ZeroPointsAdjustmentError
from ....dto.value_objects import Points
from ...base_class import Base

UPDATE_INTERVAL = timedelta(minutes=1)

if TYPE_CHECKING:
    from ..role_module import (
        Role,
        RoleEvent,
        UserRole,
    )
    from ..task_module import Task, TaskSolution
    from ..user_module import (
        UserAchievement,
        UserActivityStatus,
        UserCompetence,
        Valuation,
    )
    from .level import Level
    from .user_level import UserLevel


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
    last_active_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=False), nullable=True)
    academic_points: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    reputation_points: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    roles: Mapped[list[UserRole]] = relationship("UserRole", back_populates="user", cascade="all, delete-orphan")
    role_events_to: Mapped[list[RoleEvent]] = relationship(
        "RoleEvent", foreign_keys="RoleEvent.to_user_id", back_populates="to_user"
    )
    role_events_from: Mapped[list[RoleEvent]] = relationship(
        "RoleEvent", foreign_keys="RoleEvent.from_user_id", back_populates="from_user", cascade="all, delete-orphan"
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

    def set_initial_levels(self, levels: Sequence[Level]) -> None:
        from .user_level import UserLevel  # noqa: PLC0415

        for level in levels:
            new_link = UserLevel(level_id=level.id)
            self.user_levels.append(new_link)

    def add_role(self, role: Role) -> None:
        """
        Доменная логика: Пользователь получает роль.
        Мы проверяем, нет ли её уже, чтобы не дублировать.
        """
        from ..role_module import UserRole  # noqa: PLC0415

        # Проверяем по ID или имени, есть ли уже такая роль
        for user_role in self.roles:
            if user_role.role_id == role.id:
                return  # Роль уже есть, ничего не делаем
        # Создаем связь
        new_link = UserRole(user_id=self.id, role_id=role.id)
        self.roles.append(new_link)

    def remove_role(self, role: Role) -> None:
        """
        Доменная логика: Пользователь теряет роль.
        """
        self.roles = [ur for ur in self.roles if ur.role_id != role.id]

    def change_last_user_active(self) -> None:
        """Обновить дату последней активности пользователя"""
        self.last_active_at = datetime.now(UTC)

    def change_user_points(self, points: int, point_type: LevelTypeEnum) -> tuple[int, int]:
        """
        Изменяет очки пользователя указанного типа.
        Возвращает кортеж (int)Изменение, (int)Новое значение
        """
        if points == 0:
            raise ZeroPointsAdjustmentError()
        current = 0
        if point_type == LevelTypeEnum.ACADEMIC:
            current = self.academic_points
            self.academic_points += points
            self.academic_points = max(self.academic_points, 0)
            return self.academic_points - current, self.academic_points

        elif point_type == LevelTypeEnum.REPUTATION:
            current = self.reputation_points
            self.reputation_points += points
            self.reputation_points = max(self.reputation_points, 0)
            return self.reputation_points - current, self.reputation_points

        else:
            raise ValueError(
                f"Неизвестный тип баллов: {point_type}. Доступные типы: {[t.value for t in LevelTypeEnum]}"
            )

    def change_user_level(self, new_level_id: int, points_type: LevelTypeEnum) -> None:
        """Изменяет уровень пользователя на новый уровень указанного типа."""
        from .user_level import UserLevel  # noqa: PLC0415

        for user_level in self.user_levels:
            if user_level.level.level_type == points_type:
                user_level.level_id = new_level_id
                return

        # Если уровень указанного типа не найден, добавляем новый уровень
        new_user_level = UserLevel(level_id=new_level_id)
        self.user_levels.append(new_user_level)

    @hybrid_property
    def academic_points_vo(self) -> Points:
        """Python-side: возвращает Value Object"""
        return Points(
            value=self.academic_points,
            point_type=LevelTypeEnum.ACADEMIC,
        )

    @academic_points_vo.expression  # ty:ignore[invalid-argument-type]
    def academic_points_vo(cls) -> int:  # noqa: N805
        """SQL-side: для использования в запросах"""
        return cls.academic_points  # возвращаем базовое поле

    @academic_points_vo.setter
    def academic_points_vo(self, value: Points | int) -> None:
        """Setter: позволяет присваивать Points или int"""
        if isinstance(value, Points):
            self.academic_points = value.value
        elif isinstance(value, int):
            self.academic_points = value
        else:
            raise TypeError("academic_points_vo must be Points or int")

    # То же самое для reputation
    @hybrid_property
    def reputation_points_vo(self) -> Points:
        return Points(
            value=self.reputation_points,
            point_type=LevelTypeEnum.REPUTATION,
        )

    @reputation_points_vo.expression  # ty:ignore[invalid-argument-type]
    def reputation_points_vo(cls) -> int:  # noqa: N805
        return cls.reputation_points

    @reputation_points_vo.setter
    def reputation_points_vo(self, value: Points | int) -> None:
        if isinstance(value, Points):
            self.reputation_points = value.value
        elif isinstance(value, int):
            self.reputation_points = value
        else:
            raise TypeError("reputation_points_vo must be Points or int")
