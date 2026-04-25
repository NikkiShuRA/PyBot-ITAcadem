from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from taskiq import AsyncBroker, AsyncTaskiqDecoratedTask

from ....core.config import BotSettings
from . import broadcast, leaderboard, notification, system


@dataclass(slots=True)
class TaskRegistry:
    broadcast_task: AsyncTaskiqDecoratedTask[..., Any]
    notification_task: AsyncTaskiqDecoratedTask[..., Any]
    system_task: AsyncTaskiqDecoratedTask[..., Any]
    weekly_leaderboard_task: AsyncTaskiqDecoratedTask[..., Any]


def register_all_tasks(*, broker: AsyncBroker, settings: BotSettings) -> TaskRegistry:
    return TaskRegistry(
        broadcast_task=broadcast.register_tasks(broker=broker),
        notification_task=notification.register_tasks(broker=broker),
        system_task=system.register_tasks(broker=broker),
        weekly_leaderboard_task=leaderboard.register_tasks(broker=broker, settings=settings),
    )


__all__ = ["TaskRegistry", "register_all_tasks"]
