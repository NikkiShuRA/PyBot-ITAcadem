from collections.abc import Sequence

from sqlalchemy.ext.asyncio import AsyncSession

from ..core.config import settings
from ..core.constants import RoleEnum
from ..db.models.user_module import User
from ..domain.exceptions import (
    CompetenceNotFoundError,
    InitialLevelsNotFoundError,
    RoleNotFoundError,
    UserNotFoundError,
)
from ..dto import CompetenceReadDTO, UserCreateDTO, UserReadDTO
from ..infrastructure.competence_repository import CompetenceRepository
from ..infrastructure.level_repository import LevelRepository
from ..infrastructure.role_repository import RoleRepository
from ..infrastructure.user_repository import UserRepository
from ..mappers.competence_mappers import map_orm_competencies_to_competence_read_dtos
from ..mappers.user_mappers import map_orm_user_to_user_read_dto
from ..utils import normalize_competence_names


class UserService:
    def __init__(
        self,
        db: AsyncSession,
        user_repository: UserRepository,
        level_repository: LevelRepository,
        role_repository: RoleRepository,
        competence_repository: CompetenceRepository,
    ) -> None:
        self.db: AsyncSession = db
        self.user_repository: UserRepository = user_repository
        self.level_repository: LevelRepository = level_repository
        self.role_repository: RoleRepository = role_repository
        self.competence_repository: CompetenceRepository = competence_repository

    async def register_student(self, dto: UserCreateDTO) -> UserReadDTO:
        initial_levels = await self.level_repository.find_initial_levels(self.db)

        if not initial_levels:
            raise InitialLevelsNotFoundError()

        student_role = await self.role_repository.get_role_by_name(self.db, "Student")
        if not student_role:
            raise RoleNotFoundError("Роль 'Student' не найдена в базе данных. Сначала создайте её!")

        user = await self.user_repository.create_user_profile(self.db, data=dto)

        user.set_initial_levels(initial_levels)
        user.add_role(student_role)

        if dto.tg_id in settings.auto_admin_telegram_ids:
            admin_role = await self.role_repository.get_role_by_name(self.db, RoleEnum.ADMIN.value)
            if not admin_role:
                raise RoleNotFoundError("Роль 'Admin' не найдена в базе данных. Сначала создайте её!")
            user.add_role(admin_role)

        self.db.add(user)
        await self.db.commit()

        return await map_orm_user_to_user_read_dto(user)

    async def get_user(
        self,
        user_id: int,
    ) -> UserReadDTO:
        try:
            user = await self.user_repository.get_by_id(self.db, user_id)
        except UserNotFoundError as err:
            raise UserNotFoundError from err
        else:
            return await map_orm_user_to_user_read_dto(user)

    async def check_user_role(
        self,
        user_id: int,
        user_role: str,
    ) -> bool:
        return await self.user_repository.has_role(self.db, user_id, user_role)

    async def remove_user_role(self, tg_id: int, role_name: str) -> UserReadDTO:
        try:
            user = await self.user_repository.get_by_telegram_id(self.db, tg_id)
        except UserNotFoundError as err:
            raise UserNotFoundError(user_id=tg_id) from err

        role = await self.role_repository.get_role_by_name(self.db, role_name)

        if not role:
            raise RoleNotFoundError(f"Роль '{role_name}' не найдена в базе данных.")

        user.remove_role(role)
        await self.db.commit()

        return await map_orm_user_to_user_read_dto(user)

    async def find_user_roles(
        self,
        user_id: int,
    ) -> Sequence[str]:
        return await self.user_repository.find_user_roles(self.db, user_id)

    async def find_user_by_phone(
        self,
        phone: str,
    ) -> User | None:
        return await self.user_repository.find_user_by_phone(self.db, phone)

    async def find_user_by_telegram_id(self, tg_id: int) -> UserReadDTO | None:
        user = await self.user_repository.find_user_by_telegram_id(self.db, tg_id)
        if user:
            return await map_orm_user_to_user_read_dto(user)
        return None

    async def add_user_role(
        self,
        telegram_id: int,
        new_role: RoleEnum,
    ) -> UserReadDTO:
        try:
            user = await self.user_repository.get_by_telegram_id(self.db, telegram_id)
        except UserNotFoundError as err:
            raise UserNotFoundError(telegram_id=telegram_id) from err

        role = await self.role_repository.get_role_by_name(self.db, new_role.value)

        if not role:
            raise RoleNotFoundError(new_role.value)

        user.add_role(role)
        self.db.add(user)
        await self.db.commit()

        return await map_orm_user_to_user_read_dto(user)

    async def get_users_with_competence_id(self, competence_id: int) -> Sequence[UserReadDTO]:
        users = await self.user_repository.get_all_users_with_competence_id(self.db, competence_id)
        return [await map_orm_user_to_user_read_dto(user) for user in users]

    async def find_user_competencies(self, user_id: int) -> Sequence[CompetenceReadDTO]:
        user = await self.user_repository.find_user_by_id(self.db, user_id)
        if user is None:
            raise UserNotFoundError(user_id)

        competencies = await self.user_repository.find_all_user_competencies(self.db, user_id)
        return await map_orm_competencies_to_competence_read_dtos(competencies)

    async def add_user_competencies_by_names(self, user_id: int, competence_names: Sequence[str]) -> UserReadDTO:
        try:
            user = await self.user_repository.get_by_id(self.db, user_id)
        except UserNotFoundError as err:
            raise UserNotFoundError(user_id=user_id) from err

        normalized_names = normalize_competence_names(competence_names)
        competencies = await self.competence_repository.get_by_names(self.db, normalized_names)
        found_names = {competence.name.strip().lower() for competence in competencies}
        missing_names = [name for name in normalized_names if name not in found_names]
        if missing_names:
            raise CompetenceNotFoundError(missing_names=missing_names)

        user.add_competencies(competencies)
        await self.db.commit()
        return await map_orm_user_to_user_read_dto(user)

    async def remove_user_competencies_by_names(self, user_id: int, competence_names: Sequence[str]) -> UserReadDTO:
        try:
            user = await self.user_repository.get_by_id(self.db, user_id)
        except UserNotFoundError as err:
            raise UserNotFoundError(user_id=user_id) from err

        normalized_names = normalize_competence_names(competence_names)
        competencies = await self.competence_repository.get_by_names(self.db, normalized_names)
        found_names = {competence.name.strip().lower() for competence in competencies}
        missing_names = [name for name in normalized_names if name not in found_names]
        if missing_names:
            raise CompetenceNotFoundError(missing_names=missing_names)

        user.remove_competencies(competencies)
        await self.db.commit()
        return await map_orm_user_to_user_read_dto(user)

    async def add_user_competencies(self, user_id: int, competence_ids: Sequence[int]) -> UserReadDTO:
        try:
            user = await self.user_repository.get_by_id(self.db, user_id)
        except UserNotFoundError as err:
            raise UserNotFoundError(user_id=user_id) from err

        normalized_ids = sorted(set(competence_ids))
        if normalized_ids:
            competencies = await self.competence_repository.get_by_ids(self.db, normalized_ids)
            found_ids = {competence.id for competence in competencies}
            missing_ids = [competence_id for competence_id in normalized_ids if competence_id not in found_ids]
            if missing_ids:
                raise CompetenceNotFoundError(missing_ids=missing_ids)
            user.add_competencies(competencies)

        await self.db.commit()
        return await map_orm_user_to_user_read_dto(user)

    async def remove_user_competencies(self, user_id: int, competence_ids: Sequence[int]) -> UserReadDTO:
        try:
            user = await self.user_repository.get_by_id(self.db, user_id)
        except UserNotFoundError as err:
            raise UserNotFoundError(user_id=user_id) from err

        normalized_ids = sorted(set(competence_ids))
        if normalized_ids:
            competencies = await self.competence_repository.get_by_ids(self.db, normalized_ids)
            found_ids = {competence.id for competence in competencies}
            missing_ids = [competence_id for competence_id in normalized_ids if competence_id not in found_ids]
            if missing_ids:
                raise ValueError(f"Competence ids not found: {missing_ids}")
            user.remove_competencies(competencies)

        await self.db.commit()
        return await map_orm_user_to_user_read_dto(user)

    async def update_user_competencies(self, user_id: int, competence_ids: Sequence[int]) -> UserReadDTO:
        try:
            user = await self.user_repository.get_by_id(self.db, user_id)
        except UserNotFoundError as err:
            raise UserNotFoundError(user_id=user_id) from err

        current_competencies = await self.user_repository.find_all_user_competencies(self.db, user_id)
        user.remove_competencies(current_competencies)

        normalized_ids = sorted(set(competence_ids))
        if normalized_ids:
            competencies = await self.competence_repository.get_by_ids(self.db, normalized_ids)
            found_ids = {competence.id for competence in competencies}
            missing_ids = [competence_id for competence_id in normalized_ids if competence_id not in found_ids]
            if missing_ids:
                raise CompetenceNotFoundError(missing_ids=missing_ids)
            user.add_competencies(competencies)

        await self.db.commit()
        return await map_orm_user_to_user_read_dto(user)
