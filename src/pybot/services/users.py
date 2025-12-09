from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..core.constants import PointsTypeEnum
from ..db.models import User
from ..db.models.user_module import Level, UserLevel


async def get_user_by_telegram_id(
    db: AsyncSession,
    tg_id: int,
) -> User | None:
    result = await db.execute(select(User).where(User.telegram_id == tg_id))
    return result.scalar_one_or_none()


async def get_user_by_phone(db: AsyncSession, phone: str) -> User | None:
    res = await db.execute(select(User).where(User.phone_number == phone))
    return res.scalar_one_or_none()


async def attach_telegram_to_user(db: AsyncSession, user: User, tg_id: int) -> User:
    if user.telegram_id != tg_id:
        user.telegram_id = tg_id
        await db.commit()
        await db.refresh(user)
    return user


async def create_user_profile(  # noqa: PLR0913
    db: AsyncSession,
    *,
    phone: str,
    tg_id: int,
    first_name: str,
    last_name: str | None = None,
    patronymic: str | None = None,
) -> User:
    """Создает профиль пользователя с начальными уровнями"""

    # Получаем начальные уровни

    levels_stmt = (
        select(Level)
        .where(Level.level_type.in_([PointsTypeEnum.ACADEMIC, PointsTypeEnum.REPUTATION]))
        .order_by(Level.level_type, Level.required_points.asc())
    )

    levels_result = await db.execute(levels_stmt)
    all_levels = levels_result.scalars().unique().all()

    # Проверка что уровни найдены
    if not all_levels:
        raise ValueError("Начальные уровни не найдены в БД!")

    # Получаем только начальный уровень для каждого типа
    initial_levels = {}
    for level in all_levels:
        if level.level_type not in initial_levels:
            initial_levels[level.level_type] = level

    # Создаем пользователя
    user = User(
        phone_number=phone,
        telegram_id=tg_id,
        first_name=first_name,
        last_name=last_name,
        patronymic=patronymic,
    )

    db.add(user)
    await db.flush()

    # Добавляем ТОЛЬКО начальные уровни (по одному на каждый тип)
    for level in initial_levels.values():
        user_level = UserLevel(
            user_id=user.id,
            level_id=level.id,
        )
        db.add(user_level)

    await db.commit()
    await db.refresh(user)

    return user


async def update_user_points_by_id(db: AsyncSession, user_id: int, points: int, points_type: PointsTypeEnum) -> User:
    user_result = await db.execute(select(User).where(User.id == user_id))
    user = user_result.scalar_one_or_none()
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
