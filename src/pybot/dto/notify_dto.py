"""DTOs for outbound notifications and notification scheduling."""

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
    """Internal payload returned by the TaskIQ notification task."""

    status: NotificationStatus
    recipient_id: int
    message: str


class NotifyDTO(BaseDTO):
    """DTO for sending one outbound notification."""

    message: str
    recipient_id: int = Field(..., alias="recipient_id")
    message_thread_id: int | None = Field(None, alias="message_thread_id")
    parse_mode: str | None = None

    @field_validator("message")
    @classmethod
    def validate_message(cls, message: str) -> str:
        """Normalize and validate notification message text."""
        return normalize_message(message, max_length=4096)

    @field_validator("recipient_id")
    @classmethod
    def validate_recipient_id(cls, recipient_id: int) -> int:
        """Reject zero recipient id because Telegram does not use it."""
        if recipient_id == 0:
            raise ValueError("recipient_id must not be equal to 0")
        return recipient_id

    @field_validator("parse_mode", mode="before")
    @classmethod
    def validate_parse_mode(cls, parse_mode: str | None) -> str | None:
        """Normalize parse mode and treat empty values as ``None``."""
        if parse_mode is None:
            return None
        normalized = parse_mode.strip()
        return normalized or None


@dataclass(frozen=True, slots=True)
class NotificationLogEvent:
    """Structured log event for outbound notifications."""

    event_type: Literal["role_request_to_admin", "direct_message"]
    recipient_id: int
    message_text: str
    request_id: int | None = None
    requester_user_id: int | None = None
    role_name: str | None = None


class NotifyUserDTO(BaseDTO):
    """DTO for scheduled notification dispatch through TaskIQ."""

    model_config = ConfigDict(from_attributes=True, extra="forbid", frozen=True, arbitrary_types_allowed=True)

    recipient_id: int = Field(..., alias="recipient_id")
    message: str
    message_thread_id: int | None = None
    parse_mode: str | None = None
    kind: TaskScheduleKind
    run_at: pendulum.DateTime | None = None
    interval: timedelta | None = None
    cron: CronStr | None = None
    timezone: TimeZoneName | None = None

    @field_validator("message")
    @classmethod
    def validate_message(cls, message: str) -> str:
        """Normalize and validate notification message text."""
        return normalize_message(message, max_length=4096)

    @field_validator("recipient_id")
    @classmethod
    def validate_recipient_id(cls, recipient_id: int) -> int:
        """Reject zero recipient id because Telegram does not use it."""
        if recipient_id == 0:
            raise ValueError("recipient_id must not be equal to 0")
        return recipient_id

    @field_validator("parse_mode", mode="before")
    @classmethod
    def validate_parse_mode(cls, parse_mode: str | None) -> str | None:
        """Normalize parse mode and treat empty values as ``None``."""
        if parse_mode is None:
            return None
        normalized = parse_mode.strip()
        return normalized or None
