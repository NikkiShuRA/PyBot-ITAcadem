from collections.abc import Sequence

from sqlalchemy.ext.asyncio import AsyncSession

from ..core.constants import LevelTypeEnum
from ..db.models.user_module import Level, UserLevel
from ..infrastructure import LevelRepository


class LevelService:
    def __init__(self, level_repo: LevelRepository, db: AsyncSession) -> None:
        self.level_repo = level_repo
        self.db = db

    async def find_all_levels(self) -> Sequence[Level]:
        return await self.level_repo.find_all_levels(self.db)

    async def level_exists(self) -> bool:
        return await self.level_repo.level_exists(self.db)

    async def find_user_current_level(
        self,
        user_id: int,
        points_type: LevelTypeEnum,
    ) -> tuple[UserLevel, Level] | None:
        return await self.level_repo.find_user_current_level(self.db, user_id, points_type)

    async def find_next_level(self, current_level: Level, points_type: LevelTypeEnum) -> Level | None:
        return await self.level_repo.find_next_level(self.db, current_level, points_type)

    async def find_previous_level(self, current_level: Level, points_type: LevelTypeEnum) -> Level | None:
        return await self.level_repo.find_previous_level(self.db, current_level, points_type)
