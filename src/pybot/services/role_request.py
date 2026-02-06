from datetime import datetime, timedelta

from sqlalchemy.ext.asyncio import AsyncSession

from pybot.db.models import RoleRequest

from ..core.constants import RequestStatus
from ..domain.exceptions import (
    RoleAlreadyAssignedError,
    RoleNotFoundError,
    RoleRequestAlreadyExistsError,
    RoleRequestNotFoundError,
    UserNotFoundError,
)
from ..dto.role_dto import CreateRoleRequestDTO
from ..infrastructure import RoleRepository, RoleRequestRepository, UserRepository


class RoleRequestService:
    def __init__(
        self,
        db: AsyncSession,
        role_repository: RoleRepository,
        user_repository: UserRepository,
        role_request_repository: RoleRequestRepository,
    ) -> None:
        self.db: AsyncSession = db
        self.role_repository: RoleRepository = role_repository
        self.user_repository: UserRepository = user_repository
        self.role_request_repository: RoleRequestRepository = role_request_repository

    async def check_requesting_user(self, user_id: int, user_role: str) -> bool:
        user = await self.user_repository.get_by_id(self.db, user_id)

        if user is None:
            raise UserNotFoundError(user_id)

        role_check = await self.role_repository.get_role_by_name(self.db, user_role)

        if role_check is None:
            raise RoleNotFoundError(role_name=user_role)

        if await self.user_repository.has_role(self.db, user.id, user_role):
            raise RoleAlreadyAssignedError(role_name=user_role, user_id=user.id)

        if await self.role_request_repository.get_recent_active_request(self.db, user_id):
            raise RoleRequestAlreadyExistsError(role_name=user_role, user_id=user.id)

        last_reject = await self.role_request_repository.get_last_rejected_request(self.db, user_id)

        if not last_reject:
            return True
        else:
            return not last_reject.updated_at - datetime.now(None) < timedelta(
                seconds=5
            )  # TODO Время timedelta выставленна для тестов

    async def create_role_request(self, user_id: int, role: str) -> CreateRoleRequestDTO:
        await self.check_requesting_user(user_id, role)
        role_object = await self.role_repository.get_role_by_name(self.db, role)
        if not role_object:
            raise RoleNotFoundError(role_name=role)
        request = RoleRequest(user_id=user_id, role_id=role_object.id)
        self.db.add(request)
        await self.db.commit()
        return CreateRoleRequestDTO.model_validate(request)

    async def change_request_status(self, user_id: int, new_status: RequestStatus) -> None:
        request = await self.role_request_repository.get_recent_active_request(self.db, user_id)
        if not request:
            raise RoleRequestNotFoundError(user_id=user_id)
        request.change_status(new_status)
        self.db.add(request)
        await self.db.commit()
