from abc import ABC, abstractmethod

from ...dto.value_objects import TaskSchedule


# TODO добавить документацию
class NotificationDispatchPort(ABC):
    @abstractmethod
    async def dispatch_message(self, user_id: int, message_text: str, schedule: TaskSchedule) -> str:
        pass
