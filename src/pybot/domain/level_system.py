from .base import BaseEntityModel


class LevelSystemEntity(BaseEntityModel):
    """Доменная сущность Системы уровня."""

    id: int
    name: str
    description: str | None