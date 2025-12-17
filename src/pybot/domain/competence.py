from .base import BaseEntityModel


class CompetenceEntity(BaseEntityModel):
    """Доменная сущность Компетенции."""

    id: int
    name: str
