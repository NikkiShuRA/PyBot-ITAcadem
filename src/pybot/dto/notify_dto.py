from dataclasses import dataclass
from datetime import timedelta
from typing import Literal

import pendulum
from pydantic import ConfigDict, Field, field_validator
from pydantic_extra_types.cron import CronStr
from pydantic_extra_types.timezone_name import TimeZoneName

from ..core.constants import TaskScheduleKind
from ..utils import normalize_message
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

    @field_validator("message")
    @classmethod
    def validate_message(cls, message: str) -> str:
        """
        Валидатор параметра message.

        Проверяет, что сообщение не пустое и его длина не превышает
        максимально допустимой длины.

        Args:
            value (str): значение параметра message.

        Returns:
            str: отформатированное значение параметра message.

        Raises:
            ValueError: если сообщение пустое или его длина превышает
                максимально допустимой длины.
        """
        message = normalize_message(message)
        return message


@dataclass(frozen=True, slots=True)
class NotificationLogEvent:
    event_type: Literal["role_request_to_admin", "direct_message"]
    recipient_user_id: int
    message_text: str
    request_id: int | None = None
    requester_user_id: int | None = None
    role_name: str | None = None


class NotifyUserDTO(BaseDTO):
    model_config = ConfigDict(from_attributes=True, extra="forbid", frozen=True, arbitrary_types_allowed=True)

    user_id: int = Field(..., alias="user_id", ge=1)
    message: str
    kind: TaskScheduleKind
    run_at: pendulum.DateTime | None = None
    interval: timedelta | None = None
    cron: CronStr | None = None
    timezone: TimeZoneName | None = None

    @field_validator("message")
    @classmethod
    def validate_message(cls, message: str) -> str:
        """
        Валидатор параметра message.

        Проверяет, что сообщение не пустое и его длина не превышает
        максимально допустимой длины.

        Args:
            value (str): значение параметра message.

        Returns:
            str: отформатированное значение параметра message.

        Raises:
            ValueError: если сообщение пустое или его длина превышает
                максимально допустимой длины.
        """
        message = normalize_message(message)
        return message
