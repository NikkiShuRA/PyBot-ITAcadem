from __future__ import annotations

from typing import Any

from taskiq import AsyncBroker, AsyncTaskiqDecoratedTask


async def system_ping_task() -> str:
    """Простая smoke-задача для проверки связки worker и broker.

    Returns:
        str: Строка "pong" при успешном выполнении.
    """
    return "pong"


def register_tasks(*, broker: AsyncBroker) -> AsyncTaskiqDecoratedTask[..., Any]:
    """Регистрирует системную задачу в брокере.

    Args:
        broker: Брокер TaskIQ.

    Returns:
        AsyncTaskiqDecoratedTask: Декорированная задача.
    """
    return broker.task(task_name="system.ping")(system_ping_task)
