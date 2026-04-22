from __future__ import annotations

from typing import Any

from taskiq import AsyncBroker, AsyncTaskiqDecoratedTask


async def system_ping_task() -> str:
    """Простая smoke-задача для проверки worker/broker связки."""
    return "pong"


def register_tasks(*, broker: AsyncBroker) -> AsyncTaskiqDecoratedTask[..., Any]:
    return broker.task(task_name="system.ping")(system_ping_task)
