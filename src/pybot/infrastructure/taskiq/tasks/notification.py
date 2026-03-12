from __future__ import annotations

from dishka.integrations.taskiq import FromDishka, inject

from ....core import logger
from ....dto import NotificationTaskPayload, NotifyDTO
from ....services.ports import NotificationPermanentError, NotificationPort, NotificationTemporaryError
from ..taskiq_app import get_taskiq_broker

broker = get_taskiq_broker()


# this task intentionally performs a single delivery attempt
@broker.task(task_name="notification.send_notification_task")
@inject(patch_module=True)
async def send_notification_task(
    notification_data: NotifyDTO,
    *,
    notification_port: FromDishka[NotificationPort],
) -> NotificationTaskPayload:
    """Send a validated notification payload through the configured port.

    Args:
        notification_data: Validated notification payload to deliver.
        notification_port: The notification port to use for sending the notification.

    Returns:
        NotificationTaskPayload: Delivery status for a single attempt.
    """
    user_id, message = notification_data.user_id, notification_data.message

    try:
        logger.info("Начинаю отправку сообщения пользователю")
        await notification_port.send_message(notification_data)
        logger.info("Завершаю отправку сообщения пользователю")
    except NotificationTemporaryError:
        logger.warning("Notification temporary delivery failure for user_id={user_id}", user_id=user_id)
        return NotificationTaskPayload(status="failed_temporary", user_id=user_id, message=message)
    except NotificationPermanentError:
        logger.warning("Notification permanent delivery failure for user_id={user_id}", user_id=user_id)
        return NotificationTaskPayload(status="failed_permanent", user_id=user_id, message=message)
    else:
        return NotificationTaskPayload(status="sent", user_id=user_id, message=message)
