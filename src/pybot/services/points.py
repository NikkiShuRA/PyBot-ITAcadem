from sqlalchemy.ext.asyncio import AsyncSession

from ..core import logger
from ..core.constants import PointsTypeEnum
from ..db.models import User, Valuation
from ..db.models.user_module import UserLevel
from .levels import get_level_by_id, get_next_level, get_previous_level, get_user_current_level
from .schemas import AdjustUserPointsDTO, UpdateUserLevelDTO
from .users import get_user_by_id


async def update_user_level(db: AsyncSession, dto: UpdateUserLevelDTO) -> UserLevel:
    """Обновляет уровень пользователя, принимает DTO с данными."""
    current_user = dto.user
    current_user_level = dto.user_level
    points_type = dto.points_type
    current_points = dto.current_points
    inputed_points = dto.inputed_points

    has_level_changed = True
    # Нужна начальная ссылка на текущий уровень для проверки понижения
    current_level = await get_level_by_id(db, current_user_level.level_id)
    while has_level_changed:
        has_level_changed = False
        if inputed_points > 0:
            next_level = await get_next_level(db, current_user_level, points_type)

            # Проверяем, достаточно ли баллов для СЛЕДУЮЩЕГО уровня
            if next_level and current_points >= next_level.required_points:
                current_user_level.level_id = next_level.id
                logger.info(
                    f"Пользователь {current_user.id} повышен до уровня {next_level.name} {next_level.required_points} ({points_type.value})."  # noqa: E501
                )
                has_level_changed = True
                current_level = next_level
            elif not next_level:
                logger.info(f"Пользователь {current_user.id} достиг максимального уровня ({points_type.value}).")

        # 2. Логика понижения уровня (срабатывает только при снятии баллов)
        elif inputed_points < 0:
            # Проверяем, стало ли баллов меньше, чем нужно для ТЕКУЩЕГО уровня
            if current_points < current_level.required_points:
                previous_level = await get_previous_level(db, current_level, points_type)

                if previous_level:
                    current_user_level.level_id = previous_level.id
                    logger.info(
                        f"Пользователь {current_user.id} понижен до уровня {previous_level.name} {previous_level.required_points} ({points_type.value})."  # noqa: E501
                    )
                    has_level_changed = True
                    current_level = previous_level
                else:
                    logger.info(
                        f"Пользователь {current_user.id} на минимальном уровне ({points_type.value}) и не может быть понижен."  # noqa: E501
                    )


async def adjust_user_points(
    db: AsyncSession,
    dto: AdjustUserPointsDTO,
) -> User:
    """Изменяет баллы пользователя и обновляет уровень если необходимо."""
    recipient_id = dto.recipient_id
    giver_id = dto.giver_id
    points = dto.points
    points_type = dto.points_type
    reason = dto.reason

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

    current_level = await update_user_level(
        db,
        UpdateUserLevelDTO(
            user=recipient_user,
            user_level=current_user_level,
            points_type=points_type,
            current_points=current_points,
            inputed_points=points,
        ),
    )

    await db.commit()
    await db.refresh(recipient_user)

    action_description = "добавлены" if points >= 0 else "сняты"
    logger.info(f"Баллы {action_description}: user_id={recipient_id}, type={points_type.value}, amount={points}")

    return recipient_user
