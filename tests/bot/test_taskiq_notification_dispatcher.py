from __future__ import annotations

from datetime import UTC, datetime, timedelta
from types import SimpleNamespace
from typing import Any, cast
from unittest.mock import AsyncMock

import pytest

from pybot.core.constants import TaskScheduleKind
from pybot.dto.value_objects import TaskSchedule
from pybot.infrastructure.taskiq.taskiq_notification_dispatcher import TaskIQNotificationDispatcher


def _fake_schedule_source() -> Any:
    return cast(Any, object())


@pytest.mark.asyncio
async def test_notification_dispatcher_immediate_smoke_returns_task_id(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    fake_task = SimpleNamespace(kiq=AsyncMock(return_value=SimpleNamespace(task_id="task-42")))
    monkeypatch.setattr(TaskIQNotificationDispatcher, "_task", staticmethod(lambda: fake_task))
    dispatcher = TaskIQNotificationDispatcher(schedule_source=_fake_schedule_source())

    result = await dispatcher.dispatch_message(101, "hello", TaskSchedule.immediate())

    assert (
        result == "task-42"
    ), "Immediate dispatch lost the TaskIQ task id. Debugging queued jobs would become painful."
    fake_task.kiq.assert_awaited_once_with(user_id=101, message="hello")


@pytest.mark.asyncio
async def test_notification_dispatcher_schedules_at_specific_time_with_shared_source(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    fake_source = _fake_schedule_source()
    fake_task = SimpleNamespace(schedule_by_time=AsyncMock(return_value=SimpleNamespace(schedule_id="schedule-at-1")))
    monkeypatch.setattr(TaskIQNotificationDispatcher, "_task", staticmethod(lambda: fake_task))
    dispatcher = TaskIQNotificationDispatcher(schedule_source=fake_source)
    schedule = TaskSchedule.at(datetime(2026, 3, 8, 18, 0, tzinfo=UTC))

    result = await dispatcher.dispatch_message(202, "later", schedule)

    assert result == "schedule-at-1"
    fake_task.schedule_by_time.assert_awaited_once_with(
        fake_source,
        schedule.as_taskiq_datetime(),
        user_id=202,
        message="later",
    )


@pytest.mark.asyncio
async def test_notification_dispatcher_schedules_interval_and_cron_paths(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    fake_source = _fake_schedule_source()
    fake_interval_result = SimpleNamespace(schedule_id="schedule-interval-1")
    fake_cron_result = SimpleNamespace(schedule_id="schedule-cron-1")
    fake_kicker = SimpleNamespace(
        with_labels=lambda **kwargs: SimpleNamespace(
            schedule_by_cron=AsyncMock(return_value=fake_cron_result),
            labels=kwargs,
        )
    )
    fake_task = SimpleNamespace(
        schedule_by_interval=AsyncMock(return_value=fake_interval_result),
        kicker=lambda: fake_kicker,
    )
    monkeypatch.setattr(TaskIQNotificationDispatcher, "_task", staticmethod(lambda: fake_task))
    dispatcher = TaskIQNotificationDispatcher(schedule_source=fake_source)

    interval_result = await dispatcher.dispatch_message(303, "tick", TaskSchedule.every(timedelta(minutes=15)))
    cron_schedule = TaskSchedule.cron_based("0 9 * * *", timezone="Asia/Yekaterinburg")
    cron_result = await dispatcher.dispatch_message(404, "daily", cron_schedule)

    assert interval_result == "schedule-interval-1"
    fake_task.schedule_by_interval.assert_awaited_once_with(
        fake_source,
        timedelta(minutes=15),
        user_id=303,
        message="tick",
    )
    assert cron_result == "schedule-cron-1"


@pytest.mark.asyncio
async def test_notification_dispatcher_raises_helpful_error_on_missing_interval() -> None:
    dispatcher = TaskIQNotificationDispatcher(schedule_source=_fake_schedule_source())
    broken_schedule = TaskSchedule.model_construct(kind=TaskScheduleKind.INTERVAL, interval=None)

    with pytest.raises(ValueError, match="INTERVAL schedule requires interval"):
        await dispatcher.dispatch_message(505, "oops", broken_schedule)
