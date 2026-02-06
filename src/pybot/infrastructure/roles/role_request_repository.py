from collections.abc import Sequence

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from pybot.dto.role_dto import CreateRoleRequestDTO

from ...core.constants import RequestStatus
from ...db.models import RoleRequest


class RoleRequestRepository:
    async def get_all_role_requests(self, db: AsyncSession) -> Sequence[RoleRequest]:
        stmt = select(RoleRequest)
        result = await db.execute(stmt)
        return result.scalars().all()

    async def get_recent_active_request(self, db: AsyncSession, user_id: int) -> RoleRequest | None:
        stmt = (
            select(RoleRequest)
            .where(RoleRequest.user_id == user_id, RoleRequest.status == RequestStatus.PENDING)
            .limit(1)
        )
        result = await db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_last_rejected_request(self, db: AsyncSession, user_id: int) -> RoleRequest | None:
        stmt = (
            select(RoleRequest)
            .where(RoleRequest.user_id == user_id, RoleRequest.status == RequestStatus.REJECTED)
            .order_by(RoleRequest.created_at)
            .limit(1)
        )
        result = await db.execute(stmt)
        return result.scalar_one_or_none()

    async def create_role_request(self, db: AsyncSession, request_data: CreateRoleRequestDTO) -> RoleRequest:
        role_request = RoleRequest(**request_data.model_dump())
        return role_request
