from collections.abc import Sequence

from sqlalchemy.ext.asyncio import AsyncSession

from ..core.constants import PointsTypeEnum
from ..db.models.user_module import Level, UserLevel
from ..infrastructure import LevelRepository


class LevelService:
    """Сервис для работы с уровнями.

    Обеспечивает бизнес-логику для получения информации об уровнях и
    текущем прогрессе пользователей.
    """

    def __init__(self, level_repo: LevelRepository, db: AsyncSession) -> None:
        """Инициализирует сервис уровней.

        Args:
            level_repo: Репозиторий для работы с сущностью Level.
            db: Асинхронная сессия базы данных.
        """
        self.level_repo = level_repo
        self.db = db

    async def find_all_levels(self) -> Sequence[Level]:
        """Возвращает все доступные уровни в системе.

        Returns:
            Sequence[Level]: Последовательность объектов уровней.
        """
        return await self.level_repo.find_all_levels(self.db)

    async def level_exists(self) -> bool:
        """Проверяет, существуют ли уровни в базе данных.

        Returns:
            bool: True, если уровни существуют, иначе False.
        """
        return await self.level_repo.level_exists(self.db)

    async def find_user_current_level(
        self,
        user_id: int,
        points_type: PointsTypeEnum,
    ) -> tuple[UserLevel, Level] | None:
        """Находит текущий уровень пользователя для заданного типа очков.

        Args:
            user_id: Идентификатор пользователя.
            points_type: Тип очков для определения уровня.

        Returns:
            tuple[UserLevel, Level] | None: Кортеж из связи пользователя с уровнем и самого уровня,
                либо None, если уровень не найден.
        """
        return await self.level_repo.find_user_current_level(self.db, user_id, points_type)

    async def find_next_level(self, current_level: Level, points_type: PointsTypeEnum) -> Level | None:
        """Находит следующий уровень относительно текущего для заданного типа очков.

        Args:
            current_level: Текущий уровень.
            points_type: Тип очков.

        Returns:
            Level | None: Следующий уровень или None, если достигнут максимальный.
        """
        return await self.level_repo.find_next_level(self.db, current_level, points_type)

    async def find_previous_level(self, current_level: Level, points_type: PointsTypeEnum) -> Level | None:
        """Находит предыдущий уровень относительно текущего для заданного типа очков.

        Args:
            current_level: Текущий уровень.
            points_type: Тип очков.

        Returns:
            Level | None: Предыдущий уровень или None, если это начальный уровень.
        """
        return await self.level_repo.find_previous_level(self.db, current_level, points_type)
