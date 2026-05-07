from __future__ import annotations

from pydantic import ValidationError

from ..domain.exceptions import TaskScheduleError
from ..dto import NotifyUserDTO
from ..dto.value_objects import TaskSchedule
from .ports import NotificationDispatchPort


class NotificationFacade:
    """Фасад для отправки уведомлений.

    Обеспечивает высокоуровневый интерфейс для планирования и диспетчеризации
    уведомлений пользователям.
    """

    def __init__(self, dispatch_port: NotificationDispatchPort) -> None:
        """Инициализирует фасад уведомлений.

        Args:
            dispatch_port: Порт диспетчера уведомлений.
        """
        self._dispatch_port = dispatch_port

    async def notify_user(self, data: NotifyUserDTO) -> None:
        """Планирует отправку уведомления пользователю.

        Args:
            data: DTO с данными уведомления и параметрами планирования.

        Raises:
            TaskScheduleError: Если параметры расписания недействительны или возникла ошибка валидации.
        """
        try:
            schedule = TaskSchedule(
                kind=data.kind,
                run_at=data.run_at,
                interval=data.interval,
                cron=data.cron,
                timezone=data.timezone,
            )
        except (ValidationError, TaskScheduleError) as err:
            raise TaskScheduleError(f"Invalid notification schedule: {err}") from err

        await self._dispatch_port.dispatch_message(
            recipient_id=data.recipient_id,
            message_text=data.message,
            schedule=schedule,
            message_thread_id=data.message_thread_id,
            parse_mode=data.parse_mode,
        )
