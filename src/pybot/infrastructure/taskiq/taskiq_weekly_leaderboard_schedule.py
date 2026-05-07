from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
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
    """Спецификация для еженедельной публикации лидерборда.

    Определяет параметры расписания и получателя для задачи публикации.
    """

    recipient_id: int
    cron_expression: str
    timezone_name: str
    limit: int
    message_thread_id: int | None = None
    schedule_id: str = LEADERBOARD_WEEKLY_SCHEDULE_ID
    task_name: str = LEADERBOARD_WEEKLY_TASK_NAME


def is_expected_weekly_schedule(
    schedule: ScheduledTask,
    *,
    spec: WeeklyLeaderboardScheduleSpec,
) -> bool:
    """Проверяет, соответствует ли существующее расписание TaskIQ заданной спецификации.

    Args:
        schedule: Проверяемое расписание из TaskIQ.
        spec: Спецификация, которой должно соответствовать расписание.

    Returns:
        bool: True, если расписание соответствует спецификации, иначе False.
    """
    if schedule.task_name != spec.task_name:
        return False
    if schedule.cron != spec.cron_expression:
        return False
    if str(schedule.cron_offset) != spec.timezone_name:
        return False

    return (
        schedule.kwargs.get("recipient_id") == spec.recipient_id
        and schedule.kwargs.get("limit") == spec.limit
        and schedule.kwargs.get("message_thread_id") == spec.message_thread_id
    )


async def ensure_weekly_leaderboard_schedule(
    *,
    source: ListRedisScheduleSource,
    spec: WeeklyLeaderboardScheduleSpec,
    resolve_kicker: Callable[[], AsyncKicker[Any, Any]] | None = None,
) -> None:
    """Идемпотентно гарантирует наличие расписания еженедельного лидерборда в Redis.

    Если расписание отсутствует или не соответствует спецификации, оно будет создано или перезаписано.

    Args:
        source: Источник расписаний Redis.
        spec: Спецификация расписания.
        resolve_kicker: Функция для получения объекта Kicker для постановки задачи.

    Raises:
        RuntimeError: Если kicker не сконфигурирован.
    """
    if resolve_kicker is None:
        raise RuntimeError("Weekly leaderboard kicker resolver is not configured.")

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
            message_thread_id=spec.message_thread_id,
        )
    )
    logger.info(
        "событие=leaderboard_weekly_ensure status=created schedule_id={schedule_id}",
        schedule_id=spec.schedule_id,
    )
