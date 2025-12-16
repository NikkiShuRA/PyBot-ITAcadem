from collections.abc import Sequence

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..core.constants import PointsTypeEnum
from ..db.models import User, Valuation
from ..db.models.user_module import UserLevel
from .levels import get_all_levels
from .schemas import UserCreateDTO, UserReadDTO


async def get_user_by_id(db: AsyncSession, user_id: int) -> UserReadDTO | None:
    """Получить пользователя по ID"""
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if user:
        return UserReadDTO.model_validate(user)
    else:
        return None


async def get_user_by_telegram_id(db: AsyncSession, tg_id: int) -> User | None:
    """Получить пользователя по Telegram ID"""
    result = await db.execute(select(User).where(User.telegram_id == tg_id))
    user = result.scalar_one_or_none()
    if user:
        return UserReadDTO.model_validate(user)
    else:
        return None


async def get_user_by_phone(db: AsyncSession, phone: str) -> User | None:
    """Получить пользователя по номеру телефона"""
    res = await db.execute(select(User).where(User.phone_number == phone))
    user = res.scalar_one_or_none()
    if user:
        return UserReadDTO.model_validate(user)
    else:
        return None


async def get_all_users(db: AsyncSession) -> Sequence[User]:
    """Получить всех пользователей"""
    result = await db.execute(select(User))
    user_list = result.scalars().all()
    if user_list:
        return [UserReadDTO.model_validate(user) for user in user_list]


async def get_user_point_history_by_id(
    db: AsyncSession,
    user_id: int,
    points_type: PointsTypeEnum,
    selection_limit: int = 10,
) -> Sequence[Valuation]:
    """Получить историю изменения баллов пользователю по ID"""
    result = await db.execute(
        select(Valuation)
        .where(Valuation.recipient_id == user_id)
        .filter(Valuation.points_type == points_type)
        .order_by(Valuation.created_at.desc())
        .limit(selection_limit)
    )
    return result.scalars().all()


async def attach_telegram_to_user(db: AsyncSession, user: User, tg_id: int) -> User:  # TODO Добавить доменный объект
    """Привязать Telegram ID к пользователю"""
    if user.telegram_id != tg_id:
        user.telegram_id = tg_id
        await db.commit()
        await db.refresh(user)
    return user


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

    return UserReadDTO.model_validate(user)


async def update_user_points_by_id(
    db: AsyncSession,
    user_id: int,
    points: int,
    points_type: PointsTypeEnum,
) -> User:
    """Обновить баллы пользователя"""
    user = await get_user_by_id(db, user_id)
    if user is None:
        raise ValueError(f"Пользователь с ID {user_id} не найден.")

    if points_type == PointsTypeEnum.ACADEMIC:
        user.academic_points = points
    elif points_type == PointsTypeEnum.REPUTATION:
        user.reputation_points = points
    else:
        raise ValueError("Неизвестный тип баллов.")

    await db.commit()
    await db.refresh(user)
    return user
