from __future__ import annotations

from collections.abc import Callable
from typing import TYPE_CHECKING

from ...core.constants import TaskScheduleKind
from ...domain.exceptions import TaskScheduleUnknownKindError
from ...dto import NotifyDTO
from ...dto.value_objects import TaskSchedule
from ...services.ports import NotificationDispatchPort

if TYPE_CHECKING:
    from taskiq import AsyncTaskiqDecoratedTask
    from taskiq_redis import ListRedisScheduleSource

    from ...dto import NotificationTaskPayload


class TaskIQNotificationDispatcher(NotificationDispatchPort):
    def __init__(
        self,
        schedule_source: ListRedisScheduleSource | None = None,
        notification_task_resolver: Callable[[], AsyncTaskiqDecoratedTask[..., NotificationTaskPayload]] | None = None,
    ) -> None:
        self._schedule_source = schedule_source or self._resolve_schedule_source()
        self._notification_task_resolver = notification_task_resolver or self._resolve_notification_task

    @staticmethod
    def _resolve_schedule_source() -> ListRedisScheduleSource:
        from .taskiq_app import get_taskiq_schedule_source  # noqa: PLC0415

        return get_taskiq_schedule_source()

    @staticmethod
    def _resolve_notification_task() -> AsyncTaskiqDecoratedTask[..., NotificationTaskPayload]:
        from .taskiq_app import get_taskiq_notification_task  # noqa: PLC0415

        return get_taskiq_notification_task()

    def _task(self) -> AsyncTaskiqDecoratedTask[..., NotificationTaskPayload]:
        return self._notification_task_resolver()

    async def dispatch_message(
        self,
        recipient_id: int,
        message_text: str,
        schedule: TaskSchedule,
        parse_mode: str | None = None,
    ) -> str:
        notification_task = self._task()

        match schedule.kind:
            case TaskScheduleKind.IMMEDIATE:
                result = await notification_task.kiq(
                    NotifyDTO(recipient_id=recipient_id, message=message_text, parse_mode=parse_mode)
                )
                return result.task_id
            case TaskScheduleKind.AT:
                created = await notification_task.schedule_by_time(
                    self._schedule_source,
                    schedule.as_taskiq_datetime(),
                    notification_data=NotifyDTO(
                        recipient_id=recipient_id,
                        message=message_text,
                        parse_mode=parse_mode,
                    ),
                )
                return created.schedule_id
            case TaskScheduleKind.INTERVAL:
                created = await notification_task.schedule_by_interval(
                    self._schedule_source,
                    schedule.as_interval(),
                    notification_data=NotifyDTO(
                        recipient_id=recipient_id,
                        message=message_text,
                        parse_mode=parse_mode,
                    ),
                )
                return created.schedule_id
            case TaskScheduleKind.CRON:
                created = await (
                    notification_task.kicker()
                    .with_labels(cron_offset=schedule.as_timezone_name())
                    .schedule_by_cron(
                        self._schedule_source,
                        schedule.as_cron_expression(),
                        notification_data=NotifyDTO(
                            recipient_id=recipient_id,
                            message=message_text,
                            parse_mode=parse_mode,
                        ),
                    )
                )
                return created.schedule_id
            case _:
                raise TaskScheduleUnknownKindError(schedule.kind)
