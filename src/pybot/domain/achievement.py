from .base import BaseEntityModel


class AchievementEntity(BaseEntityModel):
    """Доменная сущность Достижения."""

    id: int
    name: str
    icon_url: str | None = None
