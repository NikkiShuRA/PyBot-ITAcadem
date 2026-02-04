from collections.abc import Sequence

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..core.constants import PointsTypeEnum, RoleEnum
from ..db.models import User
from ..db.models.user_module import UserLevel
from ..domain.exceptions import InitialLevelsNotFoundError, RoleNotFoundError, UserNotFoundError
from ..dto import UserCreateDTO, UserReadDTO
from ..infrastructure.level_repository import LevelRepository
from ..infrastructure.role_repository import RoleRepository
from ..infrastructure.user_repository import UserRepository
from ..mappers.user_mappers import map_orm_user_to_user_read_dto
from .levels import get_all_levels


class UserService:
    def __init__(
        self,
        db: AsyncSession,
        user_repository: UserRepository,
        level_repository: LevelRepository,
        role_repository: RoleRepository,
    ) -> None:
        self.db: AsyncSession = db
        self.user_repository: UserRepository = user_repository
        self.level_repository: LevelRepository = level_repository
        self.role_repository: RoleRepository = role_repository

    async def register_student(self, dto: UserCreateDTO) -> UserReadDTO:
        initial_levels = await self.level_repository.get_initial_levels(self.db)

        if not initial_levels:
            raise InitialLevelsNotFoundError()

        student_role = await self.role_repository.get_role_by_name(self.db, "Student")
        if not student_role:
            raise RoleNotFoundError("Роль 'Student' не найдена в базе данных. Сначала создайте её!")

        user = await self.user_repository.create_user_profile(self.db, data=dto)

        user.set_initial_levels(initial_levels)
        user.add_role(student_role)
        self.db.add(user)

        await self.db.commit()

        return await map_orm_user_to_user_read_dto(user)

    async def get_user(
        self,
        user_id: int,
    ) -> User | None:
        # Проверяем, есть ли пользователь
        user = await self.user_repository.get_by_id(self.db, user_id)

        if user:
            return user

        return None

    async def check_user_role(
        self,
        user_id: int,
        user_role: str,
    ) -> bool:
        """Проверить, имеет ли пользователь заданную роль."""
        return await self.user_repository.has_role(self.db, user_id, user_role)

    async def set_user_role(self, user_id: int, role_name: str) -> None:
        """Присвоить роль пользователю"""

        user = await self.user_repository.get_by_id(self.db, user_id)
        if not user:
            raise UserNotFoundError(user_id=user_id)

        role = await self.role_repository.get_role_by_name(self.db, role_name)

        if not role:
            raise RoleNotFoundError(f"Роль '{role_name}' не найдена в базе данных. Сначала создайте её!")

        user.add_role(role)

        await self.db.commit()

    async def remove_user_role(self, tg_id: int, role_name: str) -> UserReadDTO | None:
        """Удалить роль у пользователя"""

        # 1. Получаем пользователя (обязательно с подгруженными ролями!)
        user = await self.user_repository.get_by_telegram_id(self.db, tg_id)
        if not user:
            raise UserNotFoundError(user_id=user_id)

        role = await self.role_repository.get_role_by_name(self.db, role_name)

        if not role:
            raise RoleNotFoundError(f"Роль '{role_name}' не найдена в базе данных.")

        # 3. Делегируем логику Агрегату
        user.remove_role(role)

        # 4. Коммит
        await self.db.commit()

        return await map_orm_user_to_user_read_dto(user)

    async def get_user_roles(
        self,
        user_id: int,
    ) -> Sequence[str]:
        """Получить все роли пользователя."""
        return await self.user_repository.get_user_roles(self.db, user_id)

    async def get_user_by_phone(
        self,
        phone: str,
    ) -> User | None:
        return await self.user_repository.get_user_by_phone(self.db, phone)

    async def get_user_by_telegram_id(self, tg_id: int) -> UserReadDTO | None:
        user = await self.user_repository.get_user_by_telegram_id(self.db, tg_id)
        if user:
            return await map_orm_user_to_user_read_dto(user)
        else:
            return None

    async def add_user_role(
        self,
        telegram_id: int,
        new_role: RoleEnum,
    ) -> UserReadDTO:
        """
        Изменить роль пользователя.

        Args:
            telegram_id: ID пользователя в Telegram
            new_role: Новая роль (Student, Mentor, Admin)
            reason: Причина изменения (опционально)

        Returns:
            Обновленные данные пользователя

        Raises:
            UserNotFoundError: Если пользователь не найден
            RoleNotFoundError: Если роль не существует
            InvalidRoleChangeError: Если изменение роли невозможно
        """
        # Получаем пользователя
        user = await self.user_repository.get_by_telegram_id(self.db, telegram_id)
        if not user:
            raise UserNotFoundError(telegram_id=telegram_id)

        role = await self.role_repository.get_role_by_name(self.db, new_role.value)

        if not role:
            raise RoleNotFoundError(new_role.value)

        user.add_role(role)

        self.db.add(user)

        await self.db.commit()

        return await map_orm_user_to_user_read_dto(user)


async def get_user_by_telegram_id(db: AsyncSession, tg_id: int) -> UserReadDTO | None:
    """Получить пользователя по Telegram ID"""
    result = await db.execute(select(User).where(User.telegram_id == tg_id))
    user = result.scalar_one_or_none()
    if user:
        return await map_orm_user_to_user_read_dto(user)
    else:
        return None


async def create_user_profile(
    db: AsyncSession,
    *,
    data: UserCreateDTO,
) -> UserReadDTO:
    """Создает профиль пользователя с начальными уровнями"""

    # Получаем все уровни
    all_levels = await get_all_levels(db)

    if not all_levels:
        raise ValueError("Начальные уровни не найдены в БД!")

    # Получаем только начальный уровень для каждого типа
    initial_levels = {}
    for level in all_levels:
        if level.level_type not in initial_levels:
            initial_levels[level.level_type] = level

    # Создаем пользователя
    user = User(
        phone_number=data.phone,
        telegram_id=data.tg_id,
        first_name=data.first_name,
        last_name=data.last_name,
        patronymic=data.patronymic,
    )

    db.add(user)
    await db.flush()

    # Добавляем ТОЛЬКО начальные уровни
    for level in initial_levels.values():
        user_level = UserLevel(user_id=user.id, level_id=level.id)
        db.add(user_level)

    await db.commit()
    await db.refresh(user)

    return await map_orm_user_to_user_read_dto(user)


async def update_user_points_by_id(
    db: AsyncSession,
    user_id: int,
    points_value: int,
    points_type: PointsTypeEnum,
) -> UserReadDTO:
    """Обновить баллы пользователя"""
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if user is None:
        raise ValueError(f"Пользователь с ID {user_id} не найден.")

    if points_type == PointsTypeEnum.ACADEMIC:
        user.academic_points += points_value
        user.academic_points = max(user.academic_points, 0)
    elif points_type == PointsTypeEnum.REPUTATION:
        user.reputation_points += points_value
        user.reputation_points = max(user.reputation_points, 0)
    else:
        raise ValueError("Неизвестный тип баллов.")

    await db.commit()
    await db.refresh(user)
    return await map_orm_user_to_user_read_dto(user)
