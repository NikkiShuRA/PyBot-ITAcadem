from datetime import datetime, timedelta

from sqlalchemy.ext.asyncio import AsyncSession

from ..bot.texts import role_request_user_status
from ..core.config import settings
from ..core.constants import RequestStatus
from ..db.models.role_module import RoleRequest
from ..domain.exceptions import (
    RoleAlreadyAssignedError,
    RoleNotFoundError,
    RoleRequestAlreadyExistsError,
    RoleRequestAlreadyProcessedError,
    RoleRequestCooldownError,
    RoleRequestNotFoundError,
    UserNotFoundError,
)
from ..dto import NotifyDTO
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

    def get_time_since_last_reject(self, request_time: datetime, last_reject: RoleRequest) -> timedelta:
        """Return elapsed time between request creation and the latest rejected role request."""
        return request_time - last_reject.updated_at

    def get_role_request_available_at(self, last_reject: RoleRequest) -> datetime:
        """Return the moment when a new role request becomes available."""
        return last_reject.updated_at + timedelta(minutes=settings.role_request_reject_cooldown_minutes)

    async def check_requesting_user(self, user_id: int, user_role: str) -> bool:
        try:
            user = await self.user_repository.get_by_id(self.db, user_id)
        except UserNotFoundError as err:
            raise UserNotFoundError(user_id) from err

        role_check = await self.role_repository.find_role_by_name(self.db, user_role)
        if role_check is None:
            raise RoleNotFoundError(role_name=user_role)

        if await self.user_repository.has_role(self.db, user.id, user_role):
            raise RoleAlreadyAssignedError(role_name=user_role, user_id=user.id)

        if await self.role_request_repository.find_recent_active_request(self.db, user_id):
            raise RoleRequestAlreadyExistsError(role_name=user_role, user_id=user.id)

        last_reject = await self.role_request_repository.find_last_rejected_request(self.db, user_id)
        if not last_reject:
            return True

        request_time = datetime.now(None)
        available_at = self.get_role_request_available_at(last_reject)
        if request_time < available_at:
            raise RoleRequestCooldownError(user_id=user.id, role_name=user_role, available_at=available_at)

        return True

    async def create_role_request(self, user_id: int, role: str) -> CreateRoleRequestDTO:
        await self.check_requesting_user(user_id, role)

        role_object = await self.role_repository.find_role_by_name(self.db, role)
        if not role_object:
            raise RoleNotFoundError(role_name=role)

        request = RoleRequest(user_id=user_id, role_id=role_object.id)
        self.db.add(request)

        try:
            user = await self.user_repository.get_by_id(self.db, user_id)
        except UserNotFoundError as err:
            raise UserNotFoundError(user_id) from err

        await self.db.commit()
        await self.notification_service.send_role_request_to_admin(request.id, user.telegram_id, role)
        return CreateRoleRequestDTO.model_validate(request)

    async def change_request_status(self, request_id: int, new_status: RequestStatus) -> None:
        request = await self.role_request_repository.find_request_by_id(self.db, request_id)
        if request is None:
            raise RoleRequestNotFoundError()
        if request.status != RequestStatus.PENDING:
            raise RoleRequestAlreadyProcessedError()

        try:
            user = await self.user_repository.get_by_id(self.db, request.user_id)
        except UserNotFoundError as err:
            raise UserNotFoundError() from err

        role_name = request.role.name
        if new_status == RequestStatus.APPROVED and await self.user_repository.has_role(self.db, user.id, role_name):
            raise RoleAlreadyAssignedError(user_id=user.id, role_name=role_name)

        request.change_status(new_status)
        if request.status == RequestStatus.APPROVED:
            user.add_role(request.role)

        self.db.add(request)
        await self.db.commit()
        await self.notification_service.send_message(
            NotifyDTO(
                message=role_request_user_status(request.role.name, request.status),
                user_id=user.telegram_id,
            )
        )
