from sqlalchemy.ext.asyncio import AsyncSession

from ...core.config import settings
from ...core.constants import RoleEnum
from ...domain.exceptions import InitialLevelsNotFoundError, RoleNotFoundError, UserNotFoundError
from ...dto import UserCreateDTO, UserReadDTO
from ...infrastructure.level_repository import LevelRepository
from ...infrastructure.role_repository import RoleRepository
from ...infrastructure.user_repository import UserRepository
from ...mappers.user_mappers import map_orm_user_to_user_read_dto


class UserService:
    def __init__(
        self,
        db: AsyncSession,
        user_repository: UserRepository,
        level_repository: LevelRepository,
        role_repository: RoleRepository,
    ) -> None:
        self.db: AsyncSession = db
        self.user_repository: UserRepository = user_repository
        self.level_repository: LevelRepository = level_repository
        self.role_repository: RoleRepository = role_repository

    async def register_student(self, dto: UserCreateDTO) -> UserReadDTO:
        initial_levels = await self.level_repository.find_initial_levels(self.db)

        if not initial_levels:
            raise InitialLevelsNotFoundError()

        student_role = await self.role_repository.find_role_by_name(self.db, "Student")
        if not student_role:
            raise RoleNotFoundError("Роль 'Student' не найдена в базе данных. Сначала создайте её!")

        user = await self.user_repository.create_user_profile(self.db, data=dto)
        user.set_initial_levels(initial_levels)
        user.add_role(student_role)

        if dto.tg_id in settings.auto_admin_telegram_ids:
            admin_role = await self.role_repository.find_role_by_name(self.db, RoleEnum.ADMIN.value)
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
            raise UserNotFoundError(user_id) from err
        else:
            return await map_orm_user_to_user_read_dto(user)

    async def find_all_user_roles(self, user_id: int) -> set[str] | None:
        roles = await self.user_repository.find_all_user_roles_by_pk(self.db, user_id)
        return roles if roles else None

    async def find_user_by_phone(
        self,
        phone: str,
    ) -> UserReadDTO | None:
        user = await self.user_repository.find_user_by_phone(self.db, phone)
        if user:
            return await map_orm_user_to_user_read_dto(user)
        return None

    async def find_user_by_telegram_id(self, tg_id: int) -> UserReadDTO | None:
        user = await self.user_repository.find_user_by_telegram_id(self.db, tg_id)
        if user:
            return await map_orm_user_to_user_read_dto(user)
        return None

    async def track_activity(self, telegram_id: int) -> int | None:
        user = await self.user_repository.find_user_by_telegram_id(self.db, telegram_id)
        if not user:
            return None

        await self.user_repository.update_user_last_active(self.db, user.id)
        await self.db.commit()
        return user.id
