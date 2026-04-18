from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from importlib import import_module
from typing import TYPE_CHECKING, Any

from ...core import logger

if TYPE_CHECKING:
    from taskiq.kicker import AsyncKicker
    from taskiq.scheduler.scheduled_task import ScheduledTask
    from taskiq_redis import ListRedisScheduleSource

LEADERBOARD_WEEKLY_SCHEDULE_ID = "leaderboard:weekly"
LEADERBOARD_WEEKLY_TASK_NAME = "leaderboard.publish_weekly"


@dataclass(slots=True)
class WeeklyLeaderboardScheduleSpec:
    recipient_id: int
    cron_expression: str
    timezone_name: str
    limit: int
    schedule_id: str = LEADERBOARD_WEEKLY_SCHEDULE_ID
    task_name: str = LEADERBOARD_WEEKLY_TASK_NAME


def resolve_publish_weekly_leaderboard_kicker() -> AsyncKicker[Any, Any]:
    task_module = import_module(".tasks.leaderboard", package=__package__)
    task = task_module.publish_weekly_leaderboard_task
    return task.kicker()


def is_expected_weekly_schedule(
    schedule: ScheduledTask,
    *,
    spec: WeeklyLeaderboardScheduleSpec,
) -> bool:
    if schedule.task_name != spec.task_name:
        return False
    if schedule.cron != spec.cron_expression:
        return False
    if str(schedule.cron_offset) != spec.timezone_name:
        return False

    return schedule.kwargs.get("recipient_id") == spec.recipient_id and schedule.kwargs.get("limit") == spec.limit


async def ensure_weekly_leaderboard_schedule(
    *,
    source: ListRedisScheduleSource,
    spec: WeeklyLeaderboardScheduleSpec,
    resolve_kicker: Callable[[], AsyncKicker[Any, Any]] = resolve_publish_weekly_leaderboard_kicker,
) -> None:
    """Idempotently ensure one weekly leaderboard cron schedule in Redis source."""
    existing_schedule = next(
        (item for item in await source.get_schedules() if item.schedule_id == spec.schedule_id), None
    )

    if existing_schedule is not None and is_expected_weekly_schedule(
        existing_schedule,
        spec=spec,
    ):
        logger.info(
            "событие=leaderboard_weekly_ensure status=up_to_date schedule_id={schedule_id}",
            schedule_id=spec.schedule_id,
        )
        return

    if existing_schedule is not None:
        await source.delete_schedule(spec.schedule_id)
        logger.info(
            "событие=leaderboard_weekly_ensure status=replaced schedule_id={schedule_id}",
            schedule_id=spec.schedule_id,
        )

    await (
        resolve_kicker()
        .with_schedule_id(spec.schedule_id)
        .with_labels(cron_offset=spec.timezone_name)
        .schedule_by_cron(
            source,
            spec.cron_expression,
            recipient_id=spec.recipient_id,
            limit=spec.limit,
        )
    )
    logger.info(
        "событие=leaderboard_weekly_ensure status=created schedule_id={schedule_id}",
        schedule_id=spec.schedule_id,
    )
