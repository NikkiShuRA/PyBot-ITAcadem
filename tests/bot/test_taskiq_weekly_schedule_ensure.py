from __future__ import annotations

from types import SimpleNamespace
from typing import cast
from unittest.mock import AsyncMock

import pytest

from taskiq import AsyncBroker
from taskiq_redis import ListRedisScheduleSource

from pybot.core.config import BotSettings
from pybot.infrastructure.taskiq import taskiq_app


class FakeScheduleSource:
    def __init__(self, schedules: list[SimpleNamespace] | None = None) -> None:
        self.get_schedules = AsyncMock(return_value=schedules or [])
        self.delete_schedule = AsyncMock()


class FakeKicker:
    def __init__(self) -> None:
        self.schedule_id: str | None = None
        self.labels: dict[str, str | float] = {}
        self.calls: list[tuple[object, str, dict[str, int]]] = []

    def with_schedule_id(self, schedule_id: str) -> "FakeKicker":
        self.schedule_id = schedule_id
        return self

    def with_labels(self, **labels: str | float) -> "FakeKicker":
        self.labels = labels
        return self

    async def schedule_by_cron(
        self,
        source: object,
        cron: str,
        **kwargs: int,
    ) -> SimpleNamespace:
        self.calls.append((source, cron, kwargs))
        return SimpleNamespace(schedule_id=self.schedule_id)


def _weekly_settings() -> SimpleNamespace:
    return SimpleNamespace(
        leaderboard_weekly_enabled=True,
        leaderboard_weekly_recipient_id=-100_500_700,
        leaderboard_weekly_thread_id=None,
        leaderboard_weekly_cron="0 9 * * 1",
        leaderboard_weekly_timezone="Asia/Yekaterinburg",
        leaderboard_weekly_limit=10,
    )


@pytest.mark.asyncio
async def test_ensure_weekly_leaderboard_schedule_skips_outside_scheduler_process() -> None:
    settings = _weekly_settings()
    broker = SimpleNamespace(is_scheduler_process=False)
    source = FakeScheduleSource()

    await taskiq_app.ensure_weekly_leaderboard_schedule(
        broker=cast(AsyncBroker, broker),
        schedule_source=cast(ListRedisScheduleSource, source),
        settings=cast(BotSettings, settings),
    )

    source.get_schedules.assert_not_called()
    source.delete_schedule.assert_not_called()


@pytest.mark.asyncio
async def test_ensure_weekly_leaderboard_schedule_noops_when_existing_schedule_matches(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    settings = _weekly_settings()
    broker = SimpleNamespace(is_scheduler_process=True)
    kicker = FakeKicker()
    existing = SimpleNamespace(
        schedule_id=taskiq_app.LEADERBOARD_WEEKLY_SCHEDULE_ID,
        task_name=taskiq_app.LEADERBOARD_WEEKLY_TASK_NAME,
        cron="0 9 * * 1",
        cron_offset="Asia/Yekaterinburg",
        kwargs={"recipient_id": -100_500_700, "limit": 10, "message_thread_id": None},
    )
    source = FakeScheduleSource([existing])
    monkeypatch.setattr(taskiq_app, "_resolve_publish_weekly_leaderboard_kicker", lambda: kicker)

    await taskiq_app.ensure_weekly_leaderboard_schedule(
        broker=cast(AsyncBroker, broker),
        schedule_source=cast(ListRedisScheduleSource, source),
        settings=cast(BotSettings, settings),
    )

    source.get_schedules.assert_awaited_once()
    source.delete_schedule.assert_not_called()
    assert kicker.calls == []


@pytest.mark.asyncio
async def test_ensure_weekly_leaderboard_schedule_replaces_stale_schedule(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    settings = _weekly_settings()
    broker = SimpleNamespace(is_scheduler_process=True)
    kicker = FakeKicker()
    stale = SimpleNamespace(
        schedule_id=taskiq_app.LEADERBOARD_WEEKLY_SCHEDULE_ID,
        task_name=taskiq_app.LEADERBOARD_WEEKLY_TASK_NAME,
        cron="0 10 * * 1",
        cron_offset="Asia/Yekaterinburg",
        kwargs={"recipient_id": -100_500_700, "limit": 99},
    )
    source = FakeScheduleSource([stale])
    monkeypatch.setattr(taskiq_app, "_resolve_publish_weekly_leaderboard_kicker", lambda: kicker)

    await taskiq_app.ensure_weekly_leaderboard_schedule(
        broker=cast(AsyncBroker, broker),
        schedule_source=cast(ListRedisScheduleSource, source),
        settings=cast(BotSettings, settings),
    )

    source.delete_schedule.assert_awaited_once_with(taskiq_app.LEADERBOARD_WEEKLY_SCHEDULE_ID)
    assert kicker.schedule_id == taskiq_app.LEADERBOARD_WEEKLY_SCHEDULE_ID
    assert kicker.labels == {"cron_offset": "Asia/Yekaterinburg"}
    assert len(kicker.calls) == 1
    source_arg, cron_arg, kwargs_arg = kicker.calls[0]
    assert source_arg is source
    assert cron_arg == "0 9 * * 1"
    assert kwargs_arg == {
        "recipient_id": -100_500_700,
        "limit": 10,
        "message_thread_id": None,
    }
