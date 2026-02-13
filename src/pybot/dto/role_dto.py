from pydantic import Field

from ..core.constants import RequestStatus
from .base_dto import BaseDTO


class CreateRoleRequestDTO(BaseDTO):
    user_id: int = Field(..., alias="user_id", ge=1)
    role_id: int = Field(..., alias="role_id", ge=1)
    status: RequestStatus = Field(RequestStatus.PENDING, alias="status")
