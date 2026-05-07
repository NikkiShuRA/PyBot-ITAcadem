from collections.abc import Sequence
from datetime import UTC, datetime, timedelta

from sqlalchemy import and_, or_, select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from ..db.models import Competence, Role, User, UserCompetence, UserLevel, UserRole
from ..domain.exceptions import UserNotFoundError, UsersNotFoundError
from ..dto import UserCreateDTO

ACTIVITY_UPDATE_INTERVAL = timedelta(minutes=1)


class UserRepository:
    """Репозиторий для управления пользователями (User) и их атрибутами (роли, компетенции, уровни)."""

    async def get_by_id(
        self,
        db: AsyncSession,
        id_: int,
    ) -> User:
        """Получает пользователя по его внутреннему ID.

        Загружает связанные роли, компетенции и уровни.

        Args:
            db: Асинхронная сессия базы данных.
            id_: Внутренний идентификатор пользователя.

        Returns:
            User: Объект пользователя.

        Raises:
            UserNotFoundError: Если пользователь не найден.
        """
        stmt = (
            select(User)
            .options(
                selectinload(User.roles),
                selectinload(User.user_levels).joinedload(UserLevel.level),
                selectinload(User.competencies),
            )
            .where(User.id == id_)
        )
        result = await db.execute(stmt)
        user = result.scalar_one_or_none()

        if not user:
            raise UserNotFoundError(user_id=id_)

        return user

    async def get_by_telegram_id(
        self,
        db: AsyncSession,
        tg_id: int,
    ) -> User:
        """Получает пользователя по его Telegram ID.

        Args:
            db: Асинхронная сессия базы данных.
            tg_id: Telegram ID пользователя.

        Returns:
            User: Объект пользователя.

        Raises:
            UserNotFoundError: Если пользователь не найден.
        """
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
        """Получает список всех пользователей.

        Args:
            db: Асинхронная сессия базы данных.

        Returns:
            Sequence[User]: Список всех пользователей.

        Raises:
            UsersNotFoundError: Если в системе нет ни одного пользователя.
        """
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
        """Получает всех пользователей, имеющих указанную роль.

        Args:
            db: Асинхронная сессия базы данных.
            role_name: Название роли.

        Returns:
            Sequence[User]: Список пользователей с данной ролью.

        Raises:
            UsersNotFoundError: Если пользователи с такой ролью не найдены.
        """
        stmt = (
            select(User)
            .join(UserRole, UserRole.user_id == User.id)
            .join(Role, Role.id == UserRole.role_id)
            .where(Role.name == role_name)
            .options(selectinload(User.roles))
        )
        result = await db.execute(stmt)

        users = result.scalars().all()

        if not users:
            raise UsersNotFoundError()

        return users

    async def find_all_user_competencies(self, db: AsyncSession, user_id: int) -> Sequence[Competence]:
        """Возвращает список всех компетенций пользователя.

        Args:
            db: Асинхронная сессия базы данных.
            user_id: Внутренний ID пользователя.

        Returns:
            Sequence[Competence]: Список компетенций, отсортированный по имени.
        """
        stmt = (
            select(Competence)
            .select_from(UserCompetence)
            .join(Competence, UserCompetence.competence_id == Competence.id)
            .where(UserCompetence.user_id == user_id)
            .order_by(Competence.name.asc())
        )
        result = await db.execute(stmt)
        return result.scalars().all()

    async def get_all_users_with_competence_id(self, db: AsyncSession, competence_id: int) -> Sequence[User]:
        """Получает список пользователей, обладающих указанной компетенцией.

        Args:
            db: Асинхронная сессия базы данных.
            competence_id: ID компетенции.

        Returns:
            Sequence[User]: Список пользователей.

        Raises:
            UsersNotFoundError: Если пользователи с такой компетенцией не найдены.
        """
        stmt = (
            select(User)
            .join(UserCompetence, UserCompetence.user_id == User.id)
            .where(UserCompetence.competence_id == competence_id)
            .options(selectinload(User.competencies).joinedload(UserCompetence.competence))
        )
        result = await db.execute(stmt)
        users = result.scalars().all()

        if not users:
            raise UsersNotFoundError()

        return users

    async def find_all_user_roles_by_pk(self, db: AsyncSession, user_id: int) -> set[str]:
        """Возвращает множество имен ролей пользователя.

        Args:
            db: Асинхронная сессия базы данных.
            user_id: Внутренний ID пользователя.

        Returns:
            set[str]: Множество названий ролей.
        """
        stmt = select(Role.name).select_from(UserRole).join(Role).where(UserRole.user_id == user_id)
        result = await db.execute(stmt)
        return set(result.scalars().all())

    async def find_user_by_phone(
        self,
        db: AsyncSession,
        phone: str,
    ) -> User | None:
        """Находит пользователя по номеру телефона.

        Args:
            db: Асинхронная сессия базы данных.
            phone: Номер телефона.

        Returns:
            User | None: Объект пользователя или None.
        """
        stmt = select(User).where(User.phone_number == phone)
        result = await db.execute(stmt)
        user = result.scalar_one_or_none()

        return user

    async def find_user_by_telegram_id(self, db: AsyncSession, tg_id: int) -> User | None:
        """Находит пользователя по Telegram ID.

        Args:
            db: Асинхронная сессия базы данных.
            tg_id: Telegram ID пользователя.

        Returns:
            User | None: Объект пользователя или None.
        """
        stmt = select(User).where(User.telegram_id == tg_id)
        result = await db.execute(stmt)
        user = result.scalar_one_or_none()

        return user

    async def find_user_by_id(self, db: AsyncSession, user_id: int) -> User | None:
        """Находит пользователя по внутреннему ID (без загрузки связей).

        Args:
            db: Асинхронная сессия базы данных.
            user_id: Внутренний ID пользователя.

        Returns:
            User | None: Объект пользователя или None.
        """
        stmt = select(User).where(User.id == user_id)
        result = await db.execute(stmt)
        user = result.scalar_one_or_none()

        return user

    async def create_user_profile(
        self,
        db: AsyncSession,
        *,
        data: UserCreateDTO,
    ) -> User:
        """Создает новый профиль пользователя.

        Args:
            db: Асинхронная сессия базы данных.
            data: DTO с данными для создания пользователя.

        Returns:
            User: Созданный объект пользователя.
        """
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
        user_id: int,
        role_name: str,
    ) -> bool:
        """Проверяет наличие указанной роли у пользователя.

        Args:
            db: Асинхронная сессия базы данных.
            user_id: Внутренний ID пользователя.
            role_name: Название роли.

        Returns:
            bool: True, если у пользователя есть такая роль, иначе False.
        """
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

    async def find_user_roles(
        self,
        db: AsyncSession,
        user_id: int,
    ) -> Sequence[str]:
        """Возвращает список названий ролей пользователя.

        Args:
            db: Асинхронная сессия базы данных.
            user_id: Внутренний ID пользователя.

        Returns:
            Sequence[str]: Список названий ролей.
        """
        roles_stmt = select(Role.name).join(UserRole).where(UserRole.user_id == user_id)
        roles_result = await db.execute(roles_stmt)
        return roles_result.scalars().all()

    async def update_user_last_active(
        self,
        db: AsyncSession,
        user_id: int,
    ) -> None:
        """Обновляет время последней активности пользователя, если прошел интервал.

        Args:
            db: Асинхронная сессия базы данных.
            user_id: Внутренний ID пользователя.
        """
        now = datetime.now(UTC).replace(tzinfo=None)
        threshold = now - ACTIVITY_UPDATE_INTERVAL

        stmt = (
            update(User)
            .where(User.id == user_id)
            .where(or_(User.last_active_at.is_(None), User.last_active_at < threshold))
            .values(last_active_at=now)
        )

        await db.execute(stmt)
