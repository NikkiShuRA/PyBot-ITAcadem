from collections.abc import Mapping

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql.base import Executable

from ...services.ports.health_probe import SupportsExecute


class SessionExecutor(SupportsExecute):
    """Thin adapter that exposes AsyncSession.execute for health checks."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def execute(
        self,
        statement: Executable,
        params: Mapping[str, object] | None = None,
        *,
        execution_options: Mapping[str, object] | None = None,
        bind_arguments: Mapping[str, object] | None = None,
        **kwargs: object,
    ) -> object:
        _ = execution_options, bind_arguments, kwargs
        return await self._session.execute(statement, params=params)
