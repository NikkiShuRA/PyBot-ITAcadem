from sqlalchemy.ext.asyncio import AsyncSession

from ...core.config import BotSettings
from ...core.constants import RoleEnum
from ...domain.exceptions import (
    InitialLevelsNotFoundError,
    RoleNotFoundError,
)
from ...dto import UserReadDTO, UserRegistrationDTO
from ...infrastructure.competence_repository import CompetenceRepository
from ...infrastructure.level_repository import LevelRepository
from ...infrastructure.role_repository import RoleRepository
from ...infrastructure.user_repository import UserRepository
from ...mappers.user_mappers import map_orm_user_to_user_read_dto


class UserRegistrationService:
    def __init__(  # noqa: PLR0913
        self,
        db: AsyncSession,
        user_repository: UserRepository,
        level_repository: LevelRepository,
        role_repository: RoleRepository,
        competence_repository: CompetenceRepository,
        settings: BotSettings,
    ) -> None:
        self.db: AsyncSession = db
        self.user_repository: UserRepository = user_repository
        self.level_repository: LevelRepository = level_repository
        self.role_repository: RoleRepository = role_repository
        self.competence_repository: CompetenceRepository = competence_repository
        self._settings = settings

    async def register_student(self, dto: UserRegistrationDTO) -> UserReadDTO:
        initial_levels = await self.level_repository.find_initial_levels(self.db)

        if not initial_levels:
            raise InitialLevelsNotFoundError()

        student_role = await self.role_repository.find_role_by_name(self.db, "Student")
        if not student_role:
            raise RoleNotFoundError("Роль 'Student' не найдена в базе данных. Сначала создайте её!")

        admin_role = None
        if dto.user.tg_id in self._settings.auto_admin_telegram_ids:
            admin_role = await self.role_repository.find_role_by_name(self.db, RoleEnum.ADMIN.value)
            if not admin_role:
                raise RoleNotFoundError("Роль 'Admin' не найдена в базе данных. Сначала создайте её!")

        competencies = []
        if dto.competence_ids:
            competencies = await self.competence_repository.get_by_ids(self.db, dto.competence_ids)

        user = await self.user_repository.create_user_profile(self.db, data=dto.user)
        user.set_initial_levels(initial_levels)
        user.add_role(student_role)
        if admin_role is not None:
            user.add_role(admin_role)

        if competencies:
            user.add_competencies(competencies)

        self.db.add(user)
        await self.db.commit()
        return await map_orm_user_to_user_read_dto(user)
