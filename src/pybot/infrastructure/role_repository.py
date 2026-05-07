from collections.abc import Sequence

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..db.models import Role
from ..domain.exceptions import RoleNotFoundByIdError


class RoleRepository:
    """Репозиторий для управления ролями (Role).

    Предоставляет методы для поиска ролей по имени, ID или получения всех доступных ролей.
    """

    async def find_role_by_name(self, db: AsyncSession, name: str) -> Role | None:
        """Находит роль по её уникальному названию.

        Args:
            db: Асинхронная сессия базы данных.
            name: Название роли.

        Returns:
            Role | None: Объект роли или None, если роль не найдена.
        """
        stmt = select(Role).where(Role.name == name)
        result = await db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_role_by_id(self, db: AsyncSession, role_id: int) -> Role:
        """Получает роль по её ID или вызывает исключение RoleNotFoundByIdError.

        Args:
            db: Асинхронная сессия базы данных.
            role_id: Идентификатор роли.

        Returns:
            Role: Найденная роль.

        Raises:
            RoleNotFoundByIdError: Если роль с таким ID не существует.
        """
        stmt = select(Role).where(Role.id == role_id)
        result = await db.execute(stmt)
        role = result.scalar_one_or_none()
        if not role:
            raise RoleNotFoundByIdError(role_id)
        return role

    async def find_all_roles(self, db: AsyncSession) -> Sequence[Role]:
        """Возвращает все роли, отсортированные по имени.

        Args:
            db: Асинхронная сессия базы данных.

        Returns:
            Sequence[Role]: Список всех доступных ролей.
        """
        stmt = select(Role).order_by(Role.name.asc())
        result = await db.execute(stmt)
        return result.scalars().all()
