"""DTO для массовых рассылок сообщений пользователям."""

from dataclasses import dataclass

from pydantic import Field, field_validator

from ..utils import normalize_message
from .base_dto import BaseDTO


@dataclass(slots=True)
class BroadcastResult:
    """Результат выполнения массовой рассылки сообщений.

    Содержит статистику по попыткам отправки и типам возникших ошибок.
    """

    attempted: int = 0
    sent: int = 0
    failed_temporary: int = 0
    failed_permanent: int = 0
    skipped_invalid_user: int = 0


class BaseBroadcastDTO(BaseDTO):
    """Базовый DTO для выполнения рассылок.

    Определяет исходное сообщение, которое будет разослано пользователям.
    """

    message: str = Field(..., alias="broadcast_message")

    @field_validator("message")
    @classmethod
    def _normalize_message(cls, message: str) -> str:
        """Нормализует текст сообщения перед отправкой."""
        message = normalize_message(message, max_length=4096)
        return message


class CompetenceBroadcastDTO(BaseBroadcastDTO):
    """DTO для рассылки сообщения пользователям с определенной компетенцией."""

    competence_id: int = Field(..., ge=1)


class RoleBroadcastDTO(BaseBroadcastDTO):
    """DTO для рассылки сообщения пользователям с определенной ролью."""

    role_name: str

    @field_validator("role_name")
    @classmethod
    def _normalize_role(cls, role_name: str) -> str:
        """Удаляет лишние пробелы из названия роли перед валидацией."""
        normalized = role_name.strip()
        if not normalized:
            raise ValueError("role_name must not be empty")
        return normalized
