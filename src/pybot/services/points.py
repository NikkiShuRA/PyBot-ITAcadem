from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..core import logger
from ..core.constants import PointsTypeEnum
from ..db.models import User, Valuation
from ..domain import LevelEntity, Points
from ..dto import AdjustUserPointsDTO, UpdateUserLevelDTO, UserReadDTO
from ..mappers.user_mappers import map_orm_user_to_user_read_dto
from .levels import get_next_level, get_previous_level, get_user_current_level


async def update_user_level(
    db: AsyncSession,
    dto: UpdateUserLevelDTO,
) -> LevelEntity:
    user = dto.user
    current_points_domain = dto.current_points
    inputed_points_domain = dto.inputed_points
    points_type = inputed_points_domain.point_type

    result = await get_user_current_level(db, user.id, points_type)
    if result is None:
        raise ValueError(f"Уровень для пользователя {user.id} не найден.")

    user_level_orm, current_level_entity = result

    has_changed = True
    while has_changed:
        has_changed = False

        if inputed_points_domain.is_positive():
            next_level_entity = await get_next_level(db, current_level_entity, points_type)
            if next_level_entity and current_points_domain.compare_to_threshold(next_level_entity.required_points):
                user_level_orm.level_id = next_level_entity.id
                logger.info(f"Пользователь {user.id} повышен до уровня {next_level_entity.name} ({points_type.value})")
                has_changed = True
                current_level_entity = next_level_entity

        elif inputed_points_domain.is_negative():
            if inputed_points_domain.compare_to_past_threshold(current_level_entity.required_points):
                prev_level_entity = await get_previous_level(db, current_level_entity, points_type)
                if prev_level_entity:
                    user_level_orm.level_id = prev_level_entity.id
                    logger.info(
                        f"Пользователь {user.id} понижен до уровня {prev_level_entity.name} ({points_type.value})"
                    )
                    has_changed = True
                    current_level_entity = prev_level_entity

    return current_level_entity


# TODO Отрефакторить эту функцию, разбив её на более мелкие и понятные части и перенести их в сервисы
async def adjust_user_points(
    db: AsyncSession,
    dto: AdjustUserPointsDTO,
) -> UserReadDTO:
    """Изменяет баллы пользователя и обновляет уровень если необходимо."""
    recipient_id = dto.recipient_id
    giver_id = dto.giver_id
    points_domain = dto.points
    points_type = points_domain.point_type
    reason = dto.reason

    recipient_user = await db.execute(select(User).where(User.id == recipient_id))
    recipient_user_orm: User | None = recipient_user.scalar_one_or_none()
    if recipient_user_orm is None:
        raise ValueError(f"Получатель с ID {recipient_id} не найден.")

    valuation = Valuation(
        recipient_id=recipient_id,
        giver_id=giver_id,
        points=points_domain.value,
        points_type=points_type,
        reason=reason,
    )
    db.add(valuation)

    current_points_value: int
    if points_type == PointsTypeEnum.ACADEMIC:
        recipient_user_orm.academic_points += points_domain.value
        current_points_value = recipient_user_orm.academic_points
    elif points_type == PointsTypeEnum.REPUTATION:
        recipient_user_orm.reputation_points += points_domain.value
        current_points_value = recipient_user_orm.reputation_points
    else:
        raise ValueError("Неизвестный тип баллов.")

    if current_points_value < 0:
        current_points_value = 0
        if points_type == PointsTypeEnum.ACADEMIC:
            recipient_user_orm.academic_points = 0
        else:
            recipient_user_orm.reputation_points = 0

    if getattr(recipient_user_orm, f"{points_type.value}_points") <= 0:
        setattr(recipient_user_orm, f"{points_type.value}_points", 0)

    result = await get_user_current_level(db, recipient_user_orm.id, points_type)

    if result is None:
        raise ValueError(f"Уровень для пользователя с ID {recipient_id} и типа {points_type.value} не найден.")

    _, current_user_level = result

    if current_user_level is None:
        raise ValueError(f"Текущий уровень для пользователя с ID {recipient_id} и типа {points_type.value} не найден.")

    user_read_dto_for_level_update = await map_orm_user_to_user_read_dto(recipient_user_orm)

    current_points_obj = Points(value=current_points_value, point_type=points_type)

    current_user_level = await update_user_level(
        db,
        UpdateUserLevelDTO(
            user=user_read_dto_for_level_update,
            current_points=current_points_obj,
            inputed_points=points_domain,
        ),
    )

    await db.commit()
    await db.refresh(recipient_user_orm)

    action_description = "добавлены" if points_domain.value >= 0 else "сняты"
    logger.info(
        f"Баллы {action_description}: user_id={recipient_id}, type={points_type.value}, amount={points_domain.value}."
    )

    logger.info(
        f"""Пользователь {recipient_user!r} получил {points_domain.value} баллов.
            Причина: {reason or "не указана"}.
            Общее количество баллов пользователя {getattr(recipient_user_orm, f"{points_type.value}_points")}."""
    )
    return await map_orm_user_to_user_read_dto(recipient_user_orm)
