from collections.abc import Sequence

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..db.models import Role
from ..domain.exceptions import RoleNotFoundByIdError


class RoleRepository:
    """
    Stateless репозиторий.
    БЕЗ хранения сессии внутри!

    Правильный подход: сессия передаётся в методы.
    """

    async def find_role_by_name(self, db: AsyncSession, name: str) -> Role | None:
        """Находит определение роли в таблице roles"""
        stmt = select(Role).where(Role.name == name)
        result = await db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_role_by_id(self, db: AsyncSession, role_id: int) -> Role:
        """Находит определение роли в таблице roles"""
        stmt = select(Role).where(Role.id == role_id)
        result = await db.execute(stmt)
        role = result.scalar_one_or_none()
        if not role:
            raise RoleNotFoundByIdError(role_id)
        return role

    async def find_all_roles(self, db: AsyncSession) -> Sequence[Role]:
        """Return all roles ordered by name for deterministic read flows."""
        stmt = select(Role).order_by(Role.name.asc())
        result = await db.execute(stmt)
        return result.scalars().all()
