from __future__ import annotations

from datetime import UTC, datetime

import pendulum
import pytest

from pybot.core.constants import TaskScheduleKind
from pybot.domain.exceptions import TaskScheduleError
from pybot.dto.value_objects import TaskSchedule
from pybot.services.notification_facade import NotificationFacade, NotifyUserDTO
from pybot.services.ports import NotificationDispatchPort, NotificationTemporaryError


class NotificationDispatchPortSpy(NotificationDispatchPort):
    def __init__(self) -> None:
        self.calls: list[tuple[int, str, TaskSchedule]] = []

    async def dispatch_message(self, user_id: int, message_text: str, schedule: TaskSchedule) -> str:
        self.calls.append((user_id, message_text, schedule))
        return "job-123"


class FailingNotificationDispatchPort(NotificationDispatchPort):
    async def dispatch_message(self, user_id: int, message_text: str, schedule: TaskSchedule) -> str:
        raise NotificationTemporaryError("temporary failure", retry_after_seconds=7.0)


@pytest.mark.asyncio
async def test_notification_facade_dispatches_prepared_schedule_to_port() -> None:
    dispatch_port = NotificationDispatchPortSpy()
    facade = NotificationFacade(dispatch_port=dispatch_port)
    dto = NotifyUserDTO(
        user_id=55,
        message="hello there",
        kind=TaskScheduleKind.AT,
        run_at=pendulum.instance(datetime(2026, 3, 8, 12, 30, tzinfo=UTC)),
    )

    await facade.notify_user(dto)

    assert len(dispatch_port.calls) == 1
    user_id, message_text, schedule = dispatch_port.calls[0]
    assert user_id == 55
    assert message_text == "hello there"
    assert schedule.kind is TaskScheduleKind.AT
    assert schedule.run_at is not None


@pytest.mark.asyncio
async def test_notification_facade_maps_invalid_schedule_to_task_schedule_error() -> None:
    facade = NotificationFacade(dispatch_port=NotificationDispatchPortSpy())
    dto = NotifyUserDTO(
        user_id=77,
        message="hello there",
        kind=TaskScheduleKind.AT,
        run_at=None,
    )

    with pytest.raises(TaskScheduleError, match="Invalid notification schedule"):
        await facade.notify_user(dto)


@pytest.mark.asyncio
async def test_notification_facade_preserves_temporary_delivery_error() -> None:
    facade = NotificationFacade(dispatch_port=FailingNotificationDispatchPort())
    dto = NotifyUserDTO(
        user_id=88,
        message="hello there",
        kind=TaskScheduleKind.IMMEDIATE,
    )

    with pytest.raises(NotificationTemporaryError) as exc_info:
        await facade.notify_user(dto)

    assert exc_info.value.message == "temporary failure"
    assert exc_info.value.retry_after_seconds == 7.0
