from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..db.models import Role


class RoleRepository:
    """
    Stateless репозиторий.
    БЕЗ хранения сессии внутри!

    Правильный подход: сессия передаётся в методы.
    """

    async def get_role_by_name(self, db: AsyncSession, name: str) -> Role | None:
        """Находит определение роли в таблице roles"""
        stmt = select(Role).where(Role.name == name)
        result = await db.execute(stmt)
        return result.scalar_one_or_none()
