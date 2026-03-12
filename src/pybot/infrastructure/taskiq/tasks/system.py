from __future__ import annotations

from ..taskiq_app import get_taskiq_broker

broker = get_taskiq_broker()


@broker.task(task_name="system.ping")
async def system_ping_task() -> str:
    """Простая smoke-задача для проверки worker/broker связки."""
    return "pong"
