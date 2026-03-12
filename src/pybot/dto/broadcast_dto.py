from dataclasses import dataclass

from pydantic import Field, field_validator

from ..utils import normalize_message
from .base_dto import BaseDTO


@dataclass(slots=True)
class BroadcastResult:
    attempted: int = 0
    sent: int = 0
    failed_temporary: int = 0
    failed_permanent: int = 0
    skipped_invalid_user: int = 0


class BaseBroadcastDTO(BaseDTO):
    message: str = Field(..., alias="broadcast_message")

    @field_validator("message")
    @classmethod
    def _normalize_message(cls, message: str) -> str:
        message = normalize_message(message)
        return message


class CompetenceBroadcastDTO(BaseBroadcastDTO):
    competence_id: int = Field(..., ge=1)


class RoleBroadcastDTO(BaseBroadcastDTO):
    role_name: str

    @field_validator("role_name")
    @classmethod
    def _normalize_role(cls, role_name: str) -> str:
        normalized = role_name.strip()
        if not normalized:
            raise ValueError("role_name must not be empty")
        return normalized
