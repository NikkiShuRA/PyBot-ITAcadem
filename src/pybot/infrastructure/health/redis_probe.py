from collections.abc import Awaitable

from redis.asyncio import Redis

from ...services.ports.health_probe import SupportsPing


class RedisPingProbe(SupportsPing):
    """Thin adapter that exposes Redis ping as a health capability."""

    def __init__(self, client: Redis) -> None:
        self._client = client

    async def ping(self) -> object:
        result = self._client.ping()
        if isinstance(result, Awaitable):
            return await result
        return result
