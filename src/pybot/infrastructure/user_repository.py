from typing import Any

from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession

from ..db.models import Role, User, UserRole


class UserRepository:
    """
    Stateless репозиторий.
    БЕЗ хранения сессии внутри!

    Правильный подход: сессия передаётся в методы.
    """

    async def get_by_id(
        self,
        db: AsyncSession,  # ← Сессия передается СЮДА
        id_: int,
    ) -> User | None:
        stmt = select(User).where(User.id == id_)
        result = await db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_telegram_id(
        self,
        db: AsyncSession,
        tg_id: int,
    ) -> User | None:
        stmt = select(User).where(User.telegram_id == tg_id)
        result = await db.execute(stmt)
        return result.scalar_one_or_none()

    async def create(
        self,
        db: AsyncSession,
        **kwargs: Any,
    ) -> User:
        user = User(**kwargs)
        db.add(user)
        await db.commit()
        await db.refresh(user)
        return user

    async def has_role(
        self,
        db: AsyncSession,
        user_id: int,
        role_name: str,
    ) -> bool:
        stmt = (
            select(1)
            .select_from(UserRole)
            .join(Role)
            .where(
                and_(
                    UserRole.user_id == user_id,
                    Role.name == role_name,
                )
            )
            .limit(1)
        )
        result = await db.execute(stmt)
        return result.scalar_one_or_none() is not None
