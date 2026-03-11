from dataclasses import dataclass
from typing import Literal

from pydantic import Field, ValidationError, field_validator

from ..core import settings
from .base_dto import BaseDTO

NotificationStatus = Literal["sent", "failed_temporary", "failed_permanent"]


@dataclass(slots=True)
class NotificationTaskPayload:
    status: NotificationStatus
    user_id: int
    message: str


class NotifyDTO(BaseDTO):
    """
    DTO для отправки уведомления пользователю.

    Поля:
        message (str): текст уведомления.
        user_id (int): идентификатор пользователя.

    """

    message: str
    user_id: int = Field(..., alias="user_id", ge=1)

    @classmethod
    @field_validator("message")
    def validate_message(cls, value: str) -> str:
        """
        Валидатор параметра message.

        Проверяет, что сообщение не пустое и его длина не превышает
        максимально допустимой длины.

        Args:
            value (str): значение параметра message.

        Returns:
            str: отформатированное значение параметра message.

        Raises:
            ValidationError: если сообщение пустое или его длина превышает
                максимально допустимой длины.
        """
        message = value.strip()

        if not message:
            raise ValidationError("Message cannot be empty")

        if len(message) > settings.broadcast_max_text_length:
            raise ValidationError(f"Message length cannot exceed {settings.broadcast_max_text_length} characters")

        return message
