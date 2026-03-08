from __future__ import annotations

from datetime import timedelta

import pendulum
from pydantic import ConfigDict, Field, ValidationError
from pydantic_extra_types.cron import CronStr
from pydantic_extra_types.timezone_name import TimeZoneName

from ..core.config import settings
from ..core.constants import TaskScheduleKind
from ..dto.base_dto import BaseDTO
from ..dto.value_objects import TaskSchedule
from .ports import NotificationDispatchPort


class NotifyUserDTO(BaseDTO):
    model_config = ConfigDict(from_attributes=True, extra="forbid", frozen=True, arbitrary_types_allowed=True)

    user_id: int = Field(gt=0)
    message: str = Field(min_length=1, max_length=settings.broadcast_max_text_length)
    kind: TaskScheduleKind
    run_at: pendulum.DateTime | None = None
    interval: timedelta | None = None
    cron: CronStr | None = None
    timezone: TimeZoneName | None = None


# TODO Добавить доменные ошибки
class NotificationFacade:
    def __init__(self, dispatch_port: NotificationDispatchPort) -> None:
        self._dispatch_port = dispatch_port

    async def notify_user(self, data: NotifyUserDTO) -> None:
        try:
            schedule = TaskSchedule(
                kind=data.kind,
                run_at=data.run_at,
                interval=data.interval,
                cron=data.cron,
                timezone=data.timezone,
            )
        except ValidationError as err:
            raise ValueError(f"Invalid notification schedule: {err}") from err
        except ValueError as err:
            raise ValueError(f"Invalid notification schedule: {err}") from err
        await self._dispatch_port.dispatch_message(user_id=data.user_id, message_text=data.message, schedule=schedule)
