from __future__ import annotations

from importlib import import_module
from typing import TYPE_CHECKING, Any

from ...core.constants import TaskScheduleKind
from ...domain.exceptions import TaskScheduleUnknownKindError
from ...dto import NotifyDTO
from ...dto.value_objects import TaskSchedule
from ...services.ports import NotificationDispatchPort

if TYPE_CHECKING:
    from taskiq_redis import ListRedisScheduleSource


class TaskIQNotificationDispatcher(NotificationDispatchPort):
    def __init__(self, schedule_source: ListRedisScheduleSource | None = None) -> None:
        if schedule_source is None:
            taskiq_app = import_module(".taskiq_app", package=__package__)
            schedule_source = taskiq_app.get_taskiq_schedule_source()
        self._schedule_source = schedule_source

    @staticmethod
    def _task() -> Any:
        # TaskIQ + Dishka currently confuses static typing on producer-side calls.
        notification_module = import_module(".tasks.notification", package=__package__)
        return notification_module.send_notification_task

    async def dispatch_message(self, user_id: int, message_text: str, schedule: TaskSchedule) -> str:
        notification_task = self._task()

        match schedule.kind:
            case TaskScheduleKind.IMMEDIATE:
                result = await notification_task.kiq(NotifyDTO(user_id=user_id, message=message_text))
                return result.task_id
            case TaskScheduleKind.AT:
                created = await notification_task.schedule_by_time(
                    self._schedule_source,
                    schedule.as_taskiq_datetime(),
                    notification_data=NotifyDTO(user_id=user_id, message=message_text),
                )
                return created.schedule_id
            case TaskScheduleKind.INTERVAL:
                created = await notification_task.schedule_by_interval(
                    self._schedule_source,
                    schedule.as_interval(),
                    notification_data=NotifyDTO(user_id=user_id, message=message_text),
                )
                return created.schedule_id
            case TaskScheduleKind.CRON:
                created = await (
                    notification_task.kicker()
                    .with_labels(cron_offset=schedule.as_timezone_name())
                    .schedule_by_cron(
                        self._schedule_source,
                        schedule.as_cron_expression(),
                        notification_data=NotifyDTO(user_id=user_id, message=message_text),
                    )
                )
                return created.schedule_id
            case _:
                raise TaskScheduleUnknownKindError(schedule.kind)
