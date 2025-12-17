from .base import BaseEntityModel


class AttachmentEntity(BaseEntityModel):
    """Доменная сущность Приложения."""

    id: int
    name: str
    content: str
    type_id: int
