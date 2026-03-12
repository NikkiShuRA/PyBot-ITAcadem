from __future__ import annotations

from pydantic import ValidationError

from ..domain.exceptions import TaskScheduleError
from ..dto import NotifyUserDTO
from ..dto.value_objects import TaskSchedule
from .ports import NotificationDispatchPort


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
        except (ValidationError, TaskScheduleError) as err:
            raise TaskScheduleError(f"Invalid notification schedule: {err}") from err

        await self._dispatch_port.dispatch_message(user_id=data.user_id, message_text=data.message, schedule=schedule)
