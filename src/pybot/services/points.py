from sqlalchemy.ext.asyncio import AsyncSession

from ..core import logger
from ..core.constants import PointsTypeEnum
from ..db.models import User, Valuation
from ..domain import LevelEntity
from ..dto import AdjustUserPointsDTO, UpdateUserLevelDTO, UserReadDTO
from .levels import get_next_level, get_previous_level, get_user_current_level


async def update_user_level(
    db: AsyncSession,
    dto: UpdateUserLevelDTO,
) -> LevelEntity:
    user = dto.user
    points_type = dto.points_type
    current_points = dto.current_points
    inputed_points = dto.inputed_points

    # Получаем оба объекта
    result = await get_user_current_level(db, user.id, points_type)
    if result is None:
        raise ValueError(f"Уровень для пользователя {user.id} не найден.")

    user_level_orm, current_level_entity = result

    has_changed = True
    while has_changed:
        has_changed = False

        if inputed_points > 0:
            next_level_entity = await get_next_level(db, current_level_entity, points_type)
            if next_level_entity and current_points >= next_level_entity.required_points:
                user_level_orm.level_id = next_level_entity.id
                # Объект уже в сессии — изменения сохранятся при commit
                logger.info(f"Пользователь {user.id} повышен до уровня {next_level_entity.name} ({points_type.value})")
                has_changed = True
                current_level_entity = next_level_entity

        elif inputed_points < 0:
            if current_points < current_level_entity.required_points:
                prev_level_entity = await get_previous_level(db, current_level_entity, points_type)
                if prev_level_entity:
                    user_level_orm.level_id = prev_level_entity.id
                    logger.info(
                        f"Пользователь {user.id} понижен до уровня {prev_level_entity.name} ({points_type.value})"
                    )
                    has_changed = True
                    current_level_entity = prev_level_entity

    # Возвращаем актуальную доменную сущность
    return current_level_entity


async def adjust_user_points(
    db: AsyncSession,
    dto: AdjustUserPointsDTO,
) -> UserReadDTO:
    """Изменяет баллы пользователя и обновляет уровень если необходимо."""
    recipient_id = dto.recipient_id
    giver_id = dto.giver_id
    points = dto.points
    points_type = dto.points_type
    reason = dto.reason

    # Получаем пользователя
    recipient_user = await db.get(User, dto.recipient_id)
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

    if getattr(recipient_user, f"{points_type.value}_points") <= 0:
        setattr(recipient_user, f"{points_type.value}_points", 0)

    # Получаем текущий уровень пользователя
    result = await get_user_current_level(db, recipient_user.id, points_type)

    if result is None:
        raise ValueError(f"Уровень для пользователя с ID {recipient_id} и типа {points_type.value} не найден.")

    _, current_user_level = result

    if current_user_level is None:
        raise ValueError(f"Текущий уровень для пользователя с ID {recipient_id} и типа {points_type.value} не найден.")

    user_dto: UserReadDTO = UserReadDTO.model_validate(recipient_user)

    current_user_level = await update_user_level(
        db,
        UpdateUserLevelDTO(
            user=user_dto,
            points_type=points_type,
            current_points=current_points,
            inputed_points=points,
        ),
    )

    await db.commit()
    await db.refresh(recipient_user)

    action_description = "добавлены" if points >= 0 else "сняты"
    logger.info(f"Баллы {action_description}: user_id={recipient_id}, type={points_type.value}, amount={points}")

    logger.info(
        f"""Пользователь {recipient_user!r} получил {points} баллов.
            Причина: {reason or "не указана"}.
            Общее количество баллов пользователя {getattr(recipient_user, f"{points_type.value}_points")}."""
    )
    return UserReadDTO.model_validate(recipient_user)
