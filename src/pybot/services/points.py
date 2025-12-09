from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..core import logger
from ..core.constants import PointsTypeEnum
from ..db.models import User, Valuation
from ..db.models.user_module import Level, UserLevel


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
    recipient = await db.execute(select(User).where(User.id == recipient_id))
    recipient_user = recipient.scalar_one_or_none()

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

    if getattr(recipient_user, f"{points_type.value}_points") < 0:
        setattr(recipient_user, f"{points_type.value}_points", 0)
        current_points = 0

    has_level_change = True
    while has_level_change:
        has_level_change = False
        # Получаем текущий уровень пользователя
        current_user_level = await db.execute(
            select(UserLevel)
            .join(Level)
            .where(UserLevel.user_id == recipient_user.id, Level.level_type == points_type)
            .order_by(Level.required_points.desc())
            .limit(1)
        )
        current_level_obj = current_user_level.scalar_one_or_none()

        if not current_level_obj:
            has_level_change = False
            continue

        current_level = await db.execute(select(Level).where(Level.id == current_level_obj.level_id))
        current_level_data = current_level.scalar_one()

        if points >= 0:
            # Ищем СЛЕДУЮЩИЙ уровень
            next_level = await db.execute(
                select(Level)
                .where(Level.level_type == points_type, Level.required_points > current_level_data.required_points)
                .order_by(Level.required_points.asc())
                .limit(1)
            )
            next_level_obj = next_level.scalar_one_or_none()

            if next_level_obj is not None and current_points >= next_level_obj.required_points:
                current_level_obj.level_id = next_level_obj.id
                has_level_change = True
                logger.info(f"Пользователь {recipient_user.id} повышен до {next_level_obj.name}")
        else:
            # Ищем ПРЕДЫДУЩИЙ уровень
            prev_level = await db.execute(
                select(Level)
                .where(Level.level_type == points_type, Level.required_points < current_level_data.required_points)
                .order_by(Level.required_points.desc())
                .limit(1)
            )
            prev_level_obj = prev_level.scalar_one_or_none()

            if prev_level_obj is not None and current_points < current_level_data.required_points:
                current_level_obj.level_id = prev_level_obj.id
                has_level_change = True
                logger.info(f"Пользователь {recipient_user.id} понижен до {prev_level_obj.name}")

    await db.commit()
    await db.refresh(recipient_user)

    action_description = "добавлены" if points >= 0 else "сняты"
    logger.info(f"Баллы {action_description}: user_id={recipient_id}, type={points_type.value}, amount={points}")

    return recipient_user
