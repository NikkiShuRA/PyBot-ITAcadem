from collections.abc import Sequence

from sqlalchemy.ext.asyncio import AsyncSession

from ...core.constants import RoleEnum
from ...domain.exceptions import RoleNotFoundError, UserNotFoundError
from ...dto import RoleReadDTO, UserReadDTO
from ...infrastructure.role_repository import RoleRepository
from ...infrastructure.user_repository import UserRepository
from ...mappers.user_mappers import map_orm_user_to_user_read_dto


class UserRolesService:
    def __init__(
        self,
        db: AsyncSession,
        user_repository: UserRepository,
        role_repository: RoleRepository,
    ) -> None:
        self.db: AsyncSession = db
        self.user_repository: UserRepository = user_repository
        self.role_repository: RoleRepository = role_repository

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
            raise UserNotFoundError(telegram_id=tg_id) from err

        role = await self.role_repository.find_role_by_name(self.db, role_name)
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

    async def find_all_roles(self) -> Sequence[RoleReadDTO]:
        roles = await self.role_repository.find_all_roles(self.db)
        return [
            RoleReadDTO(
                id=role.id,
                name=role.name,
                description=role.description,
            )
            for role in roles
        ]

    async def add_user_role(
        self,
        telegram_id: int,
        new_role: RoleEnum,
    ) -> UserReadDTO:
        try:
            user = await self.user_repository.get_by_telegram_id(self.db, telegram_id)
        except UserNotFoundError as err:
            raise UserNotFoundError(telegram_id=telegram_id) from err

        role = await self.role_repository.find_role_by_name(self.db, new_role.value)
        if not role:
            raise RoleNotFoundError(new_role.value)

        user.add_role(role)
        self.db.add(user)
        await self.db.commit()
        return await map_orm_user_to_user_read_dto(user)
