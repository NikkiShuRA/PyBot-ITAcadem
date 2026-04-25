from abc import ABC, abstractmethod

from ...dto import NotifyDTO


class NotificationPort(ABC):
    """Контракт исходящих уведомлений для сервисов приложения.

    Notes:
        Семантика `recipient_id` зависит от транспорта. В адаптерах Telegram
        это соответствует `telegram_id` / `chat_id`.
    """

    @abstractmethod
    async def send_role_request_to_admin(
        self,
        request_id: int,
        requester_user_id: int,
        role_name: str,
    ) -> None:
        """Отправляет уведомление администратору о запросе роли.

        Args:
            request_id: Уникальный идентификатор запроса роли.
            requester_user_id: Идентификатор запрашивающего пользователя.
            role_name: Запрошенная роль.

        Raises:
            NotificationTemporaryError: Временная ошибка доставки, возможен повтор.
            NotificationPermanentError: Неустранимая ошибка доставки.
        """
        pass

    @abstractmethod
    async def send_message(self, message_data: NotifyDTO) -> None:
        """Отправляет прямое сообщение одному получателю.

        Args:
            message_data: Валидированный DTO с данными сообщения и получателем.

        Raises:
            NotificationTemporaryError: Временная ошибка доставки, возможен повтор.
            NotificationPermanentError: Неустранимая ошибка доставки.
        """
        pass
