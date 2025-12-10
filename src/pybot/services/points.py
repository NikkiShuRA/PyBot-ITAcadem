from sqlalchemy.ext.asyncio import AsyncSession

from ..core import logger
from ..core.constants import PointsTypeEnum
from ..db.models import User, Valuation
from .levels import get_level_by_id, get_next_level, get_user_current_level
from .users import get_user_by_id


async def adjust_user_points(  # noqa: PLR0913, PLR0917
    db: AsyncSession,
    recipient_id: int,
    giver_id: int,
    points: int,
    points_type: PointsTypeEnum,
    reason: str | None = None,
) -> User:
    """Изменяет баллы пользователя и обновляет уровень если необходимо."""

    # Получаем пользователя
    recipient_user = await get_user_by_id(db, recipient_id)
    if recipient_user is None:
        raise ValueError(f"Получатель с ID {recipient_id} не найден.")

    # Создаём запись о транзакции
    valuation = Valuation(
        recipient_id=recipient_id,
        giver_id=giver_id,
        points=points,
        points_type=points_type,
        reason=reason,
    )
    db.add(valuation)

    # Обновляем баллы
    if points_type == PointsTypeEnum.ACADEMIC:
        recipient_user.academic_points += points
        current_points = recipient_user.academic_points
    elif points_type == PointsTypeEnum.REPUTATION:
        recipient_user.reputation_points += points
        current_points = recipient_user.reputation_points
    else:
        raise ValueError("Неизвестный тип баллов.")

    # Получаем текущий уровень пользователя
    current_user_level = await get_user_current_level(db, recipient_user.id, points_type)

    if current_user_level is None:
        raise ValueError(f"Текущий уровень для пользователя с ID {recipient_id} и типа {points_type.value} не найден.")

    current_level = await get_level_by_id(db, current_user_level.level_id)
    if current_level is None:
        raise ValueError(f"Уровень с ID {current_user_level.level_id} не найден.")

    # Проверяем, достиг ли пользователь следующего уровня
    if current_points >= current_level.required_points:
        next_level = await get_next_level(db, current_level, points_type)

        if next_level:
            current_user_level.level_id = next_level.id
            logger.info(f"Пользователь {recipient_user.id} повышен до уровня {next_level.name} ({points_type.value}).")
        else:
            logger.info(f"Пользователь {recipient_user.id} достиг максимального уровня ({points_type.value}).")

    await db.commit()
    await db.refresh(recipient_user)

    action_description = "добавлены" if points >= 0 else "сняты"
    logger.info(f"Баллы {action_description}: user_id={recipient_id}, type={points_type.value}, amount={points}")

    return recipient_user
