from ..db.models import Level
from ..dto import LevelReadDTO
from ..dto.value_objects import Points


async def map_orm_level_to_level_read_dto(orm_level: Level) -> LevelReadDTO:
    """
    Маппит ORM Level объект в LevelReadDTO.
    Конвертирует int-баллы в объекты Points.
    """
    return LevelReadDTO(
        system=orm_level.level_type,
        name=orm_level.name,
        required_points=Points(value=orm_level.required_points, point_type=orm_level.level_type),
    )
