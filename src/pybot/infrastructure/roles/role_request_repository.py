from collections.abc import Sequence

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from ...core.constants import RequestStatus
from ...db.models import RoleRequest


class RoleRequestRepository:
    """Репозиторий для управления заявками на получение роли (RoleRequest)."""

    async def find_all_role_requests(self, db: AsyncSession) -> Sequence[RoleRequest]:
        """Возвращает все заявки на роли.

        Args:
            db: Асинхронная сессия базы данных.

        Returns:
            Sequence[RoleRequest]: Список всех заявок.
        """
        stmt = select(RoleRequest)
        result = await db.execute(stmt)
        return result.scalars().all()

    async def find_recent_active_request(self, db: AsyncSession, user_id: int) -> RoleRequest | None:
        """Находит последнюю активную (PENDING) заявку пользователя.

        Args:
            db: Асинхронная сессия базы данных.
            user_id: ID пользователя.

        Returns:
            RoleRequest | None: Активная заявка или None.
        """
        stmt = (
            select(RoleRequest)
            .where(RoleRequest.user_id == user_id, RoleRequest.status == RequestStatus.PENDING)
            .order_by(RoleRequest.created_at.desc())
            .limit(1)
        )
        result = await db.execute(stmt)
        return result.scalar_one_or_none()

    async def find_last_rejected_request(self, db: AsyncSession, user_id: int) -> RoleRequest | None:
        """Находит последнюю отклоненную заявку пользователя.

        Args:
            db: Асинхронная сессия базы данных.
            user_id: ID пользователя.

        Returns:
            RoleRequest | None: Отклоненная заявка или None.
        """
        stmt = (
            select(RoleRequest)
            .where(RoleRequest.user_id == user_id, RoleRequest.status == RequestStatus.REJECTED)
            .order_by(RoleRequest.created_at.desc())
            .limit(1)
        )
        result = await db.execute(stmt)
        return result.scalar_one_or_none()

    async def find_request_by_id(self, db: AsyncSession, request_id: int) -> RoleRequest | None:
        """Находит заявку по её ID, загружая связанную роль.

        Args:
            db: Асинхронная сессия базы данных.
            request_id: ID заявки.

        Returns:
            RoleRequest | None: Обьект заявки или None.
        """
        stmt = select(RoleRequest).options(selectinload(RoleRequest.role)).where(RoleRequest.id == request_id)
        result = await db.execute(stmt)
        return result.scalar_one_or_none()
