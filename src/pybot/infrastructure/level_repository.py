from collections.abc import Sequence

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from ..core.constants import PointsTypeEnum
from ..db.models.user_module import Level, UserLevel


class LevelRepository:
    """Репозиторий для управления уровнями (Level) и связями пользователей с ними (UserLevel)."""

    async def find_all_levels(self, db: AsyncSession) -> Sequence[Level]:
        """Возвращает все существующие уровни.

        Args:
            db: Асинхронная сессия базы данных.

        Returns:
            Sequence[Level]: Список всех уровней.
        """
        stmt = select(Level)
        result = await db.execute(stmt)
        return result.scalars().all()

    async def find_all_by_type(self, db: AsyncSession, points_type: str) -> Sequence[Level]:
        """Возвращает все уровни для конкретного типа баллов.

        Args:
            db: Асинхронная сессия базы данных.
            points_type: Тип баллов (soft/hard).

        Returns:
            Sequence[Level]: Список уровней, соответствующих типу.
        """
        stmt = select(Level).where(Level.level_type == points_type)
        result = await db.execute(stmt)
        return result.scalars().all()

    async def find_initial_levels(self, db: AsyncSession) -> Sequence[Level]:
        """Возвращает уровни, не требующие баллов (нулевой уровень).

        Args:
            db: Асинхронная сессия базы данных.

        Returns:
            Sequence[Level]: Список начальных уровней.
        """
        stmt = select(Level).where(Level.required_points == 0)
        result = await db.execute(stmt)
        return result.scalars().all()

    async def level_exists(self, db: AsyncSession) -> bool:
        """Проверяет, существует ли хотя бы один уровень в базе данных.

        Args:
            db: Асинхронная сессия базы данных.

        Returns:
            bool: True, если уровни найдены, иначе False.
        """
        stmt = select(Level).limit(1)
        result = await db.execute(stmt)
        return result.scalars().first() is not None

    async def find_user_current_level(
        self,
        db: AsyncSession,
        user_id: int,
        points_type: PointsTypeEnum,
    ) -> tuple[UserLevel, Level] | None:
        """Находит текущий уровень пользователя для указанного типа баллов.

        Ищет запись в UserLevel с максимальным количеством баллов для данного типа.

        Args:
            db: Асинхронная сессия базы данных.
            user_id: Идентификатор пользователя.
            points_type: Тип баллов.

        Returns:
            tuple[UserLevel, Level] | None: Кортеж из связи и самого уровня или None.
        """
        stmt = (
            select(UserLevel)
            .options(joinedload(UserLevel.level))
            .join(Level)
            .where(
                UserLevel.user_id == user_id,
                Level.level_type == points_type,
            )
            .order_by(Level.required_points.desc())
            .limit(1)
        )
        result = await db.execute(stmt)
        user_level_orm: UserLevel | None = result.scalar_one_or_none()

        if user_level_orm is None or user_level_orm.level is None:
            return None

        return user_level_orm, user_level_orm.level

    async def find_next_level(
        self,
        db: AsyncSession,
        current_level: Level,
        points_type: PointsTypeEnum,
    ) -> Level | None:
        """Находит следующий уровень после текущего.

        Args:
            db: Асинхронная сессия базы данных.
            current_level: Объект текущего уровня.
            points_type: Тип баллов.

        Returns:
            Level | None: Следующий уровень или None, если текущий — максимальный.
        """
        stmt = (
            select(Level)
            .where(
                Level.level_type == points_type,
                Level.required_points > current_level.required_points,
            )
            .order_by(Level.required_points.asc())
            .limit(1)
        )
        result = await db.execute(stmt)
        next_level_orm = result.scalar_one_or_none()

        if next_level_orm is None:
            return None

        return next_level_orm

    async def find_previous_level(
        self,
        db: AsyncSession,
        current_level: Level,
        points_type: PointsTypeEnum,
    ) -> Level | None:
        """Находит предыдущий уровень перед текущим.

        Args:
            db: Асинхронная сессия базы данных.
            current_level: Объект текущего уровня.
            points_type: Тип баллов.

        Returns:
            Level | None: Предыдущий уровень или None, если текущий — минимальный.
        """
        query = (
            select(Level)
            .where(Level.level_type == points_type, Level.required_points < current_level.required_points)
            .order_by(Level.required_points.desc())
            .limit(1)
        )
        result = await db.execute(query)
        prev_level_orm = result.scalar_one_or_none()

        if prev_level_orm is None:
            return None

        return prev_level_orm
