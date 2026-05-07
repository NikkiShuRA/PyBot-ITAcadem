"""DTO для работы с ролями пользователей и заявками на получение ролей."""

from pydantic import Field, field_validator

from ..core.constants import RequestStatus
from .base_dto import BaseDTO


class RoleReadDTO(BaseDTO):
    """DTO для базовой информации о роли."""

    id: int = Field(..., gt=0)
    name: str = Field(..., min_length=1, max_length=100)
    description: str | None = Field(default=None, max_length=500)


class RoleByIdDTO(BaseDTO):
    """DTO для идентификации роли по ее ID."""

    role_id: int = Field(..., gt=0)


class RoleIdsDTO(BaseDTO):
    """DTO для списка идентификаторов ролей."""

    role_ids: list[int] = Field(..., min_length=1)

    @field_validator("role_ids")
    @classmethod
    def validate_role_ids(cls, value: list[int]) -> list[int]:
        """Проверяет идентификаторы ролей на положительность и удаляет дубликаты."""
        if any(role_id <= 0 for role_id in value):
            raise ValueError("All role ids must be positive integers")
        return sorted(set(value))


class CreateRoleRequestDTO(BaseDTO):
    """DTO для создания заявки на получение определённой роли пользователем."""

    user_id: int = Field(..., alias="user_id", ge=1)
    role_id: int = Field(..., alias="role_id", ge=1)
    status: RequestStatus = Field(RequestStatus.PENDING, alias="status")
