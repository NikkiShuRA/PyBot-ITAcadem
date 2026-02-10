from datetime import UTC, datetime, timedelta

from sqlalchemy import Sequence, and_, or_, select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from ..db.models import Role, User, UserRole
from ..domain.exceptions import UserNotFoundError, UsersNotFoundError
from ..dto import UserCreateDTO

ACTIVITY_UPDATE_INTERVAL = timedelta(minutes=1)


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
        stmt = select(User).options(selectinload(User.roles), selectinload(User.user_levels)).where(User.id == id_)
        result = await db.execute(stmt)
        user = result.scalar_one_or_none()

        if not user:
            raise UserNotFoundError(user_id=id_)

        return user

    async def get_by_telegram_id(
        self,
        db: AsyncSession,
        tg_id: int,
    ) -> User | None:
        stmt = (
            select(User)
            .where(User.telegram_id == tg_id)
            .options(selectinload(User.roles), selectinload(User.user_levels))
        )
        result = await db.execute(stmt)
        user = result.scalar_one_or_none()

        if not user:
            raise UserNotFoundError(telegram_id=tg_id)

        return user

    async def get_all_users(
        self,
        db: AsyncSession,
    ) -> Sequence[User]:
        stmt = select(User)
        result = await db.execute(stmt)
        users = result.scalars().all()

        if not users:
            raise UsersNotFoundError()

        return users

    async def get_all_users_with_role(
        self,
        db: AsyncSession,
        role_name: str,
    ) -> Sequence[User]:
        stmt = select(User).where(User.roles.any(Role.name == role_name)).options(selectinload(User.roles))
        result = await db.execute(stmt)

        users = result.scalars().all()

        if not users:
            raise UsersNotFoundError()

        return users

    async def get_all_user_roles_by_pk(self, db: AsyncSession, user_id: int) -> set[str]:
        stmt = select(Role.name).select_from(UserRole).join(Role).where(UserRole.user_id == user_id)
        result = await db.execute(stmt)
        return set(result.scalars().all())

    async def get_user_by_phone(
        self,
        db: AsyncSession,
        phone: str,
    ) -> User | None:
        stmt = select(User).where(User.phone_number == phone)
        result = await db.execute(stmt)
        user = result.scalar_one_or_none()

        return user

    async def get_user_by_telegram_id(self, db: AsyncSession, tg_id: int) -> User | None:
        stmt = select(User).where(User.telegram_id == tg_id)
        result = await db.execute(stmt)
        user = result.scalar_one_or_none()

        return user

    async def create_user_profile(
        self,
        db: AsyncSession,
        *,
        data: UserCreateDTO,
    ) -> User:
        user = User(
            phone_number=data.phone,
            telegram_id=data.tg_id,
            first_name=data.first_name,
            last_name=data.last_name,
            patronymic=data.patronymic,
        )
        db.add(user)
        return user

    async def has_role(
        self,
        db: AsyncSession,
        user_id: int,  # <- Меняем аргумент, мы ищем по TG ID
        role_name: str,
    ) -> bool:
        stmt = (
            select(1)
            .select_from(UserRole)
            .join(Role)
            .join(User)  # <- Добавляем JOIN с User
            .where(
                and_(
                    User.id == user_id,  # <- Сравниваем с user_id
                    Role.name == role_name,
                )
            )
            .limit(1)
        )
        result = await db.execute(stmt)
        return result.scalar_one_or_none() is not None

    async def get_user_roles(
        self,
        db: AsyncSession,
        user_id: int,
    ) -> Sequence[str]:
        stmt = select(Role.name).select_from(UserRole).join(Role).where(UserRole.user_id == user_id)
        result = await db.execute(stmt)
        return result.scalars().all()

    async def update_user_last_active(
        self,
        db: AsyncSession,
        user_id: int,
    ) -> None:
        now = datetime.now(UTC).replace(tzinfo=None)
        threshold = now - ACTIVITY_UPDATE_INTERVAL

        stmt = (
            update(User)
            .where(User.id == user_id)
            .where(or_(User.last_active_at.is_(None), User.last_active_at < threshold))
            .values(last_active_at=now)
        )

        await db.execute(stmt)
