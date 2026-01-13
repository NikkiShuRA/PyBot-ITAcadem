from aiogram_dialog import DialogManager
from pydantic import ValidationError

from ..core import logger
from ..core.constants import PointsTypeEnum
from ..db.models import User
from ..domain import LevelEntity, Points
from ..dto import UserCreateDTO, UserReadDTO
from .level_mappers import map_user_levels_to_domain_levels


async def map_orm_levels_to_domain(user: User) -> list[LevelEntity] | None:
    """
    Маппит список ORM Level объектов в список доменных LevelEntity.
    Если пользователь не найден или не имеет связанных уровней, возвращает None.
    """

    if user and hasattr(user, "user_levels"):
        return await map_user_levels_to_domain_levels(user.user_levels)
    else:
        return None


async def map_orm_user_to_user_read_dto(orm_user: User) -> UserReadDTO:
    """
    Маппит ORM User объект в UserReadDTO.
    Конвертирует int-баллы в объекты Points.
    """
    return UserReadDTO(
        id=orm_user.id,
        first_name=orm_user.first_name,
        last_name=orm_user.last_name,
        patronymic=orm_user.patronymic,
        telegram_id=orm_user.telegram_id,
        academic_points=Points(value=orm_user.academic_points, point_type=PointsTypeEnum.ACADEMIC),
        reputation_points=Points(value=orm_user.reputation_points, point_type=PointsTypeEnum.REPUTATION),
        join_date=orm_user.join_date,
    )


async def map_dialog_data_to_user_create_dto(manager: DialogManager) -> UserCreateDTO | None:
    """
    Маппинг данных из dialog_data в UserCreateDTO.
    Возвращает DTO или None, если данные неполные или невалидны.
    """
    phone = manager.dialog_data.get("phone_number")
    tg_id = manager.dialog_data.get("tg_id")
    first_name = manager.dialog_data.get("first_name")
    last_name = manager.dialog_data.get("last_name")
    patronymic = manager.dialog_data.get("patronymic")

    if not (phone and tg_id and first_name and last_name):
        logger.error(
            f"Недостаточно данных для создания профиля в dialog_data. "
            f"phone: {phone}, tg_id: {tg_id}, first_name: {first_name}, last_name: {last_name}"
        )
        return None

    try:
        user_data = UserCreateDTO(
            phone=phone,
            tg_id=tg_id,
            first_name=first_name,
            last_name=last_name,
            patronymic=patronymic,
        )
    except (ValidationError, TypeError):
        logger.exception("Ошибка валидации данных для создания профиля из dialog_data")
        await manager.done()
        return None
    else:
        return user_data
