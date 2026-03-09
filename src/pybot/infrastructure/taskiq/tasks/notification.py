from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

from dishka.integrations.taskiq import FromDishka, inject

from ....core import logger
from ....core.config import settings
from ....services.ports import NotificationPermanentError, NotificationPort, NotificationTemporaryError
from ..taskiq_app import get_taskiq_broker

broker = get_taskiq_broker()

NotificationStatus = Literal["sent", "failed_temporary", "failed_permanent"]


@dataclass(slots=True)
class NotificationTaskPayload:
    status: NotificationStatus
    user_id: int
    message: str


# TODO: перекинуть это в utils и добавить domain errors
def validate_message(message: str) -> str:
    """Validate message parameter of send_notification_task."""
    message = message.strip()

    if not message:
        raise ValueError("Message cannot be empty")

    if len(message) > settings.broadcast_max_text_length:
        raise ValueError(f"Message length cannot exceed {settings.broadcast_max_text_length} characters")

    return message


# TODO: перекинуть это в utils и добавить domain errors
def validate_user_id(user_id: int) -> int:
    """Validate user_id parameter of send_notification_task."""
    if user_id <= 0:
        raise ValueError("User ID must be greater than 0")

    return user_id


# TODO: Проверить при следующем архитектурном обходе и подумать над retry
@broker.task(task_name="notification.send_notification_task")
@inject(patch_module=True)
async def send_notification_task(
    user_id: int,
    message: str,
    *,
    notification_port: FromDishka[NotificationPort],
) -> NotificationTaskPayload:
    """TaskIQ task to send a notification to a user through a notification port.

    Args:
        user_id: The Telegram user ID of the recipient.
        message: The notification message to be sent.
        notification_port: The notification port to use for sending the notification.

    Returns:
        NotificationTaskPayload: A payload with the status of the notification delivery.
    """
    user_id = validate_user_id(user_id)
    message = validate_message(message)

    try:
        logger.info("Начинаю отправку сообщения пользователю")
        await notification_port.send_message(user_id=user_id, message_text=message)
        logger.info("Завершаю отправку сообщения пользователю")
    except NotificationTemporaryError:
        logger.warning("Notification temporary delivery failure for user_id={user_id}", user_id=user_id)
        return NotificationTaskPayload(status="failed_temporary", user_id=user_id, message=message)
    except NotificationPermanentError:
        logger.warning("Notification permanent delivery failure for user_id={user_id}", user_id=user_id)
        return NotificationTaskPayload(status="failed_permanent", user_id=user_id, message=message)
    except Exception:
        logger.exception("Notification unexpected delivery failure for user_id={user_id}", user_id=user_id)
        return NotificationTaskPayload(status="failed_permanent", user_id=user_id, message=message)
    else:
        return NotificationTaskPayload(status="sent", user_id=user_id, message=message)
