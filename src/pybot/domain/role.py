from .base import BaseEntityModel


class RoleEntity(BaseEntityModel):
    """Доменная сущность Роли (для админов и академических)."""

    id: int
    name: str
    description: str | None = None
