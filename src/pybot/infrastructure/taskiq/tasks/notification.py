from __future__ import annotations

from typing import Any

from dishka.integrations.taskiq import FromDishka, inject
from taskiq import AsyncBroker, AsyncTaskiqDecoratedTask

from ....core import logger
from ....dto import NotificationTaskPayload, NotifyDTO
from ....services.ports import NotificationPermanentError, NotificationPort, NotificationTemporaryError


async def send_notification_task(
    notification_data: NotifyDTO,
    *,
    notification_port: FromDishka[NotificationPort],
) -> NotificationTaskPayload:
    """Send a notification via configured notification port."""
    recipient_id, message = notification_data.recipient_id, notification_data.message

    try:
        logger.info(
            "событие=отправка_уведомления status=started recipient_id={recipient_id}",
            recipient_id=recipient_id,
        )
        await notification_port.send_message(notification_data)
        logger.info(
            "событие=отправка_уведомления status=sent recipient_id={recipient_id}",
            recipient_id=recipient_id,
        )
    except NotificationTemporaryError:
        logger.warning(
            "событие=отправка_уведомления status=failed_temporary recipient_id={recipient_id}",
            recipient_id=recipient_id,
        )
        return NotificationTaskPayload(status="failed_temporary", recipient_id=recipient_id, message=message)
    except NotificationPermanentError:
        logger.warning(
            "событие=отправка_уведомления status=failed_permanent recipient_id={recipient_id}",
            recipient_id=recipient_id,
        )
        return NotificationTaskPayload(status="failed_permanent", recipient_id=recipient_id, message=message)
    else:
        return NotificationTaskPayload(status="sent", recipient_id=recipient_id, message=message)


def register_tasks(*, broker: AsyncBroker) -> AsyncTaskiqDecoratedTask[..., Any]:
    return broker.task(task_name="notification.send_notification_task")(
        inject(patch_module=True)(send_notification_task)
    )
