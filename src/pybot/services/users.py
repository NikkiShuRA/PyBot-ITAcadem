from collections.abc import Sequence

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from ..core.constants import PointsTypeEnum
from ..db.models import User, Valuation
from ..db.models.user_module import UserLevel
from ..domain import Points, UserEntity, ValuationEntity
from ..dto import UserCreateDTO, UserReadDTO
from ..infrastructure.level_repository import LevelRepository
from ..infrastructure.user_repository import UserRepository
from ..mappers.points_mappers import map_orm_valuations_to_domain
from ..mappers.user_mappers import map_orm_levels_to_domain, map_orm_user_to_user_read_dto
from .levels import get_all_levels


class UserService:
    def __init__(self, db: AsyncSession, user_repository: UserRepository, level_repository: LevelRepository) -> None:
        self.db: AsyncSession = db
        self.user_repository: UserRepository = user_repository
        self.level_repository: LevelRepository = level_repository

    async def register_student(self, dto: UserCreateDTO) -> UserReadDTO:
        initial_levels = await self.level_repository.get_initial_levels(self.db)

        if not initial_levels:
            raise ValueError("В системе не настроены начальные уровни!")

        user = await self.user_repository.create_user_profile(self.db, data=dto)

        user.set_initial_levels(initial_levels)
        self.db.add(user)

        await self.db.commit()

        return await map_orm_user_to_user_read_dto(user)

    async def get_user(
        self,
        tg_id: int,
    ) -> User | None:
        # Проверяем, есть ли пользователь
        user = await self.user_repository.get_by_telegram_id(self.db, tg_id)

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

        # 1. Получаем пользователя (обязательно с подгруженными ролями!)
        # Тебе нужно убедиться, что repo.get_by_id делает .options(selectinload(User.roles))
        user = await self.user_repository.get_by_id(self.db, user_id)
        if not user:
            raise ValueError(f"User {user_id} not found")

        # 2. Получаем саму РОЛЬ (Entity)
        role = await self.user_repository.get_role_by_name(self.db, role_name)

        # ВОТ ЗДЕСЬ У ТЕБЯ ПАДАЛО
        if not role:
            # Вариант А: Упасть с ошибкой (как сейчас)
            raise ValueError(f"Роль '{role_name}' не найдена в базе данных. Сначала создайте её!")

        # 3. Делегируем логику Агрегату
        user.add_role(role)

        # 4. Коммит
        await self.db.commit()

    async def get_user_roles(
        self,
        user_id: int,
    ) -> Sequence[str]:
        """Получить все роли пользователя."""
        return await self.user_repository.get_user_roles(self.db, user_id)


async def get_user_by_id(db: AsyncSession, user_id: int) -> UserReadDTO | None:
    """Получить пользователя по ID"""
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if user:
        return await map_orm_user_to_user_read_dto(user)
    else:
        return None


async def get_user_by_telegram_id(db: AsyncSession, tg_id: int) -> UserReadDTO | None:
    """Получить пользователя по Telegram ID"""
    result = await db.execute(select(User).where(User.telegram_id == tg_id))
    user = result.scalar_one_or_none()
    if user:
        return await map_orm_user_to_user_read_dto(user)
    else:
        return None


async def get_user_by_phone(db: AsyncSession, phone: str) -> UserEntity | None:
    """Получить пользователя по номеру телефона"""
    stmt = (
        select(User)
        .options(
            joinedload(User.user_levels).joinedload(UserLevel.level),
            joinedload(User.competencies),
            joinedload(User.achievements),
            joinedload(User.created_tasks),
            joinedload(User.solutions),
        )
        .where(User.phone_number == phone)
    )
    res = await db.execute(stmt)
    user_from_orm = res.unique().scalar_one_or_none()

    if user_from_orm:
        levels_entities = await map_orm_levels_to_domain(user_from_orm)
        if levels_entities is None:
            raise ValueError("Уровни пользователя не найдены")
        # Создаём UserEntity с manual полями
        user_entity = UserEntity(
            id=user_from_orm.id,
            first_name=user_from_orm.first_name,
            last_name=user_from_orm.last_name,
            patronymic=user_from_orm.patronymic,
            telegram_id=user_from_orm.telegram_id,
            academic_points=Points(value=user_from_orm.academic_points, point_type=PointsTypeEnum.ACADEMIC),
            reputation_points=Points(value=user_from_orm.reputation_points, point_type=PointsTypeEnum.REPUTATION),
            join_date=user_from_orm.join_date,
            user_levels=levels_entities,
        )  # TODO Добавить маппинг связей с другими list связями модели
        return user_entity
    else:
        return None


async def get_all_users(db: AsyncSession) -> Sequence[UserReadDTO]:  # TODO Использовать тут mapper
    """Получить всех пользователей"""
    result = await db.execute(select(User))
    user_list = result.scalars().all()
    if user_list:
        return [await map_orm_user_to_user_read_dto(user) for user in user_list]
    else:
        raise ValueError("Пользователи не найдены")


async def get_user_point_history_by_id(
    db: AsyncSession,
    user_id: int,
    points_type: PointsTypeEnum,
    selection_limit: int = 10,
) -> Sequence[ValuationEntity]:
    """Получить историю изменения баллов пользователю по ID"""
    result = await db.execute(
        select(Valuation)
        .where(Valuation.recipient_id == user_id)
        .filter(Valuation.points_type == points_type)
        .order_by(Valuation.created_at.desc())
        .limit(selection_limit)
    )
    return await map_orm_valuations_to_domain(result.scalars().all())


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
