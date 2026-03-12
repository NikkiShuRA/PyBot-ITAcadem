from abc import ABC, abstractmethod

from ...dto.value_objects import TaskSchedule


class NotificationDispatchPort(ABC):
    """
    Интерфейс для отправки уведомлений через различный транспорт.

    Attributes:
        None

    Methods:
        dispatch_message(user_id, message_text, schedule)
            Отправляет уведомление на указанный пользователь.

            Args:
                user_id (int): Идентификатор пользователя в транспортном семантике.
                message_text (str): Текст уведомления.
                schedule (TaskSchedule): Параметры отправки уведомления.

            Returns:
                str: Уника отправки уведомления.
    """

    @abstractmethod
    async def dispatch_message(self, user_id: int, message_text: str, schedule: TaskSchedule) -> str:
        """
        Отправляет уведомление на указанный пользователь.

        Args:
            user_id (int): Идентификатор пользователя в транспортном семантике.
            message_text (str): Текст уведомления.
            schedule (TaskSchedule): Параметры отправки уведомления.

        Returns:
            str: Уника отправки уведомления.
        """
        pass
