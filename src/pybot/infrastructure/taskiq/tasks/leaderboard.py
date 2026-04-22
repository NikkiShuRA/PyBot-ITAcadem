from __future__ import annotations

from typing import Any

from dishka.integrations.taskiq import FromDishka, inject
from taskiq import AsyncBroker, AsyncTaskiqDecoratedTask

from ....core import logger
from ....core.config import BotSettings
from ....services.weekly_leaderboard_publisher import WeeklyLeaderboardPublisherService


async def publish_weekly_leaderboard_task(
    *,
    recipient_id: int,
    limit: int,
    service: FromDishka[WeeklyLeaderboardPublisherService],
    settings: FromDishka[BotSettings],
) -> dict[str, int]:
    """Publish previous-week leaderboard to configured recipient."""
    await service.publish_weekly(
        recipient_id=recipient_id,
        limit=limit,
        business_tz=str(settings.leaderboard_weekly_timezone),
    )
    payload = {
        "recipient_id": recipient_id,
        "limit": limit,
    }
    logger.info("TaskIQ weekly leaderboard task finished with payload={payload}", payload=payload)
    return payload


def register_tasks(
    *,
    broker: AsyncBroker,
    settings: BotSettings,
) -> AsyncTaskiqDecoratedTask[..., Any]:
    return broker.task(
        task_name="leaderboard.publish_weekly",
        retry_on_error=settings.leaderboard_weekly_retry_enabled,
        max_retries=settings.leaderboard_weekly_retry_max_retries,
        delay=settings.leaderboard_weekly_retry_delay_s,
    )(inject(patch_module=True)(publish_weekly_leaderboard_task))
