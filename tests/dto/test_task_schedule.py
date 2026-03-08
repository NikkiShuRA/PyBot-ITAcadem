from datetime import UTC, datetime, timedelta

import pendulum
import pytest
from pydantic import ValidationError
from pydantic_extra_types.cron import CronStr
from pydantic_extra_types.timezone_name import TimeZoneName

from pybot.core.constants import TaskScheduleKind
from pybot.dto.value_objects import TaskSchedule


def test_task_schedule_immediate_has_no_timing_fields() -> None:
    schedule = TaskSchedule.immediate()

    assert schedule.kind is TaskScheduleKind.IMMEDIATE
    assert schedule.run_at is None
    assert schedule.interval is None
    assert schedule.cron is None
    assert schedule.timezone is None


def test_task_schedule_at_converts_datetime_to_pendulum_datetime() -> None:
    source = datetime(2026, 3, 8, 12, 30, tzinfo=UTC)

    schedule = TaskSchedule.at(source)

    assert isinstance(schedule.run_at, pendulum.DateTime)
    assert schedule.run_at == pendulum.instance(source)
    assert schedule.as_taskiq_datetime() == pendulum.instance(source)


def test_task_schedule_at_rejects_naive_datetime() -> None:
    with pytest.raises(ValidationError, match="run_at must be timezone-aware"):
        TaskSchedule.at(datetime(2026, 3, 8, 12, 30))


def test_task_schedule_every_rejects_non_positive_interval() -> None:
    with pytest.raises(ValidationError, match="interval must be greater than zero"):
        TaskSchedule.every(timedelta(0))


def test_task_schedule_cron_based_accepts_valid_timezone() -> None:
    schedule = TaskSchedule.cron_based("0 9 * * *", timezone="Asia/Yekaterinburg")

    assert schedule.kind is TaskScheduleKind.CRON
    assert isinstance(schedule.cron, CronStr)
    assert isinstance(schedule.timezone, TimeZoneName)
    assert schedule.cron == "0 9 * * *"
    assert schedule.timezone == "Asia/Yekaterinburg"


def test_task_schedule_cron_based_rejects_invalid_timezone() -> None:
    with pytest.raises(ValidationError, match="Invalid timezone name"):
        TaskSchedule.cron_based("0 9 * * *", timezone="Mars/Olympus")


def test_task_schedule_cron_based_rejects_invalid_cron_expression() -> None:
    with pytest.raises(ValidationError, match="Cron expression must contain 5 space separated components"):
        TaskSchedule.cron_based("0 9 * *", timezone="UTC")
