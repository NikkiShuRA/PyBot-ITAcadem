from datetime import datetime, timedelta

from sqlalchemy.ext.asyncio import AsyncSession

from ..core.constants import RequestStatus
from ..db.models.role_module import RoleRequest
from ..domain.exceptions import (
    RoleAlreadyAssignedError,
    RoleNotFoundError,
    RoleRequestAlreadyExistsError,
    RoleRequestAlreadyProcessedError,
    RoleRequestNotFoundError,
    RoleRequestRejectedError,
    UserNotFoundError,
)
from ..dto.role_dto import CreateRoleRequestDTO
from ..infrastructure import RoleRepository, RoleRequestRepository, UserRepository
from ..services.ports import NotificationPort


class RoleRequestService:
    def __init__(
        self,
        db: AsyncSession,
        role_repository: RoleRepository,
        user_repository: UserRepository,
        role_request_repository: RoleRequestRepository,
        notification_service: NotificationPort,
    ) -> None:
        self.db: AsyncSession = db
        self.role_repository: RoleRepository = role_repository
        self.user_repository: UserRepository = user_repository
        self.role_request_repository: RoleRequestRepository = role_request_repository
        self.notification_service: NotificationPort = notification_service

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
            return not (datetime.now(None) - last_reject.updated_at) < timedelta(
                seconds=5
            )  # TODO Время timedelta выставленна для тестов

    async def create_role_request(self, user_id: int, role: str) -> CreateRoleRequestDTO:
        if not await self.check_requesting_user(user_id, role):
            raise RoleRequestRejectedError(role_name=role, user_id=user_id)

        role_object = await self.role_repository.get_role_by_name(self.db, role)

        if not role_object:
            raise RoleNotFoundError(role_name=role)

        request = RoleRequest(user_id=user_id, role_id=role_object.id)
        self.db.add(request)

        user = await self.user_repository.get_by_id(self.db, user_id)
        if user is None:
            raise UserNotFoundError(user_id)

        await self.db.commit()
        await self.notification_service.send_role_request_to_admin(request.id, user.telegram_id, role)

        return CreateRoleRequestDTO.model_validate(request)

    async def change_request_status(self, request_id: int, new_status: RequestStatus) -> None:
        request = await self.role_request_repository.get_request_by_id(self.db, request_id)
        if request is None:
            raise RoleRequestNotFoundError()
        if request.status != RequestStatus.PENDING:
            raise RoleRequestAlreadyProcessedError()
        user = await self.user_repository.get_by_id(self.db, request.user_id)
        if user is None:
            raise UserNotFoundError()
        role_name = request.role.name
        if new_status == RequestStatus.APPROVED and await self.user_repository.has_role(self.db, user.id, role_name):
            raise RoleAlreadyAssignedError(user_id=user.id, role_name=role_name)
        request.change_status(new_status)
        if request.status == RequestStatus.APPROVED:
            user.add_role(request.role)
        self.db.add(request)
        await self.db.commit()
        await self.notification_service.send_message(
            user_id=user.telegram_id,
            message_text=f"Ваша заявка на роль {request.role.name} была {request.status.name}",
        )
