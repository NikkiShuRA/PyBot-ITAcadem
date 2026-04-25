from collections.abc import Awaitable

from redis.asyncio import Redis

from ...services.ports.health_probe import SupportsPing


class RedisPingProbe(SupportsPing):
    """Адаптер для Redis, реализующий интерфейс SupportsPing.

    Используется для проверки доступности Redis в рамках системных проверок здоровья.
    """

    def __init__(self, client: Redis) -> None:
        """Инициализирует адаптер Redis.

        Args:
            client: Экземпляр асинхронного клиента Redis.
        """
        self._client = client

    async def ping(self) -> object:
        """Выполняет команду PING к Redis.

        Returns:
            object: Результат команды PING.
        """
        result = self._client.ping()
        if isinstance(result, Awaitable):
            return await result
        return result
