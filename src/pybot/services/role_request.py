from datetime import datetime, timedelta

from sqlalchemy.ext.asyncio import AsyncSession

from ..core.config import BotSettings
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
from ..presentation.texts import role_request_user_status
from ..services.ports import NotificationPort


class RoleRequestService:
    """Сервис управления запросами на получение ролей.

    Обеспечивает создание запросов, проверку кулдаунов и изменение статусов запросов.
    """

    def __init__(  # noqa: PLR0913
        self,
        db: AsyncSession,
        role_repository: RoleRepository,
        user_repository: UserRepository,
        role_request_repository: RoleRequestRepository,
        notification_service: NotificationPort,
        settings: BotSettings,
    ) -> None:
        """Инициализирует сервис запросов ролей.

        Args:
            db: Асинхронная сессия базы данных.
            role_repository: Репозиторий для работы с ролями.
            user_repository: Репозиторий для работы с пользователями.
            role_request_repository: Репозиторий для работы с запросами ролей.
            notification_service: Сервис уведомлений.
            settings: Настройки бота.
        """
        self.db: AsyncSession = db
        self.role_repository: RoleRepository = role_repository
        self.user_repository: UserRepository = user_repository
        self.role_request_repository: RoleRequestRepository = role_request_repository
        self.notification_service: NotificationPort = notification_service
        self._settings = settings

    def get_time_since_last_reject(self, request_time: datetime, last_reject: RoleRequest) -> timedelta:
        """Возвращает время, прошедшее между созданием запроса и последним отклоненным запросом.

        Args:
            request_time: Время текущего запроса.
            last_reject: Последний отклоненный запрос.

        Returns:
            timedelta: Прошедшее время.
        """
        return request_time - last_reject.updated_at

    def get_role_request_available_at(self, last_reject: RoleRequest) -> datetime:
        """Возвращает момент времени, когда будет доступен новый запрос роли.

        Args:
            last_reject: Последний отклоненный запрос роли.

        Returns:
            datetime: Время, после которого можно создать новый запрос.
        """
        return last_reject.updated_at + timedelta(minutes=self._settings.role_request_reject_cooldown_minutes)

    async def check_requesting_user(self, user_id: int, user_role: str) -> bool:
        """Проверяет возможность пользователя запросить указанную роль.

        Args:
            user_id: Идентификатор пользователя.
            user_role: Название запрашиваемой роли.

        Raises:
            UserNotFoundError: Если пользователь не найден.
            RoleNotFoundError: Если роль не найдена.
            RoleAlreadyAssignedError: Если роль уже назначена пользователю.
            RoleRequestAlreadyExistsError: Если у пользователя уже есть активный запрос на эту роль.
            RoleRequestCooldownError: Если не истек кулдаун после предыдущего отклонения.

        Returns:
            bool: True, если пользователь может запросить роль.
        """
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
        """Создает новый запрос на получение роли.

        Args:
            user_id: Идентификатор пользователя.
            role: Название запрашиваемой роли.

        Raises:
            RoleNotFoundError: Если роль не найдена.
            UserNotFoundError: Если пользователь не найден.

        Returns:
            CreateRoleRequestDTO: DTO с данными созданного запроса.
        """
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
        """Изменяет статус запроса на роль.

        Args:
            request_id: Идентификатор запроса.
            new_status: Новый статус запроса (RequestStatus).

        Raises:
            RoleRequestNotFoundError: Если запрос не найден.
            RoleRequestAlreadyProcessedError: Если запрос уже был обработан.
            UserNotFoundError: Если пользователь, сделавший запрос, не найден.
            RoleAlreadyAssignedError: Если роль уже назначена пользователю (при попытке одобрить).
        """
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
                recipient_id=user.telegram_id,
            )
        )
