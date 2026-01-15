from .base import BaseEntityModel


class LevelEventReasonTypeEntity(BaseEntityModel):
    """Доменная сущность Тип причины оценки."""

    id: int
    name: str   
    description: str | None
