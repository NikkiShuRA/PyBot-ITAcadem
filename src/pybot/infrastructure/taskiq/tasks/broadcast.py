from __future__ import annotations

from dishka.integrations.taskiq import FromDishka, inject

from ....core import logger
from ....dto import BroadcastDTO
from ....services.broadcast import BroadcastService
from ..taskiq_app import get_taskiq_broker

broker = get_taskiq_broker()


@broker.task(task_name="broadcast.send_for_all")
@inject(patch_module=True)
async def broadcast_for_all_task(
    message: str,
    service: FromDishka[BroadcastService],
) -> dict[str, int]:
    """
    Отложенная массовая рассылка для всех пользователей.

    Задача выполняется в worker-процессе и использует тот же сервисный слой,
    что и aiogram-хендлеры, но через отдельный request-scope DI-контейнера.
    """

    result = await service.broadcast_for_all(BroadcastDTO(broadcast_message=message))

    payload = {
        "attempted": result.attempted,
        "sent": result.sent,
        "failed_temporary": result.failed_temporary,
        "failed_permanent": result.failed_permanent,
        "skipped_invalid_user": result.skipped_invalid_user,
    }
    logger.info("TaskIQ broadcast task finished with payload={payload}", payload=payload)
    return payload
