from collections.abc import Sequence

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ...core.constants import RequestStatus
from ...db.models import RoleRequest


class RoleRequestRepository:
    """
    Репозиторий для работы с RoleRequest.

    Attributes:
        _session_factory (Session): Фабрика для создания сессии БД

    Methods:
        get_all_role_requests (db: AsyncSession) -> Sequence[RoleRequest]: Получает все RoleRequest
        get_recent_active_request (db: AsyncSession, user_id: int) -> RoleRequest | None: Получает последнюю активную
        RoleRequest для пользователя
        get_last_rejected_request (db: AsyncSession, user_id: int) -> RoleRequest | None: Получает последнюю отклонённую
        RoleRequest для пользователя
    """

    async def get_all_role_requests(self, db: AsyncSession) -> Sequence[RoleRequest]:
        stmt = select(RoleRequest)
        result = await db.execute(stmt)
        return result.scalars().all()

    async def get_recent_active_request(self, db: AsyncSession, user_id: int) -> RoleRequest | None:
        stmt = (
            select(RoleRequest)
            .where(RoleRequest.user_id == user_id, RoleRequest.status == RequestStatus.PENDING)
            .order_by(RoleRequest.created_at.desc())
            .limit(1)
        )
        result = await db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_last_rejected_request(self, db: AsyncSession, user_id: int) -> RoleRequest | None:
        stmt = (
            select(RoleRequest)
            .where(RoleRequest.user_id == user_id, RoleRequest.status == RequestStatus.REJECTED)
            .order_by(RoleRequest.created_at.desc())
            .limit(1)
        )
        result = await db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_request_by_id(self, db: AsyncSession, request_id: int) -> RoleRequest | None:
        stmt = select(RoleRequest).where(RoleRequest.id == request_id)
        result = await db.execute(stmt)
        return result.scalar_one_or_none()
