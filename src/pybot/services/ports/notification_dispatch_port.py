from abc import ABC, abstractmethod

from ...dto.value_objects import TaskSchedule


class NotificationDispatchPort(ABC):
    """Контракт для диспетчеризации уведомлений через фоновый процесс."""

    @abstractmethod
    async def dispatch_message(
        self,
        recipient_id: int,
        message_text: str,
        schedule: TaskSchedule,
        message_thread_id: int | None = None,
        parse_mode: str | None = None,
    ) -> str:
        """Отправляет уведомление в соответствии с предоставленным расписанием.

        Args:
            recipient_id: Идентификатор получателя (семантика зависит от транспорта).
            message_text: Текст уведомления.
            schedule: Настройки расписания для доставки.
            message_thread_id: Опциональный идентификатор темы (топика) для супергрупп.
            parse_mode: Опциональный режим парсинга (например, HTML/Markdown). Если None,
                адаптеры не должны его использовать при вызове транспортного слоя.

        Returns:
            str: Идентификатор задачи для поставленного в очередь/запланированного уведомления.
        """
        pass
