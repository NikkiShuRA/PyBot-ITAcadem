from collections.abc import Mapping

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql.base import Executable

from ...services.ports.health_probe import SupportsExecute


class SessionExecutor(SupportsExecute):
    """Адаптер для асинхронной сессии SQLAlchemy, реализующий интерфейс SupportsExecute.

    Позволяет выполнять SQL-запросы в рамках проверок работоспособности базы данных.
    """

    def __init__(self, session: AsyncSession) -> None:
        """Инициализирует адаптер сессии.

        Args:
            session: Асинхронная сессия SQLAlchemy.
        """
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
        """Выполняет SQL-запрос.

        Args:
            statement: Объект запроса SQLAlchemy.
            params: Параметры запроса.
            execution_options: Опции выполнения.
            bind_arguments: Аргументы связывания.
            **kwargs: Дополнительные аргументы.

        Returns:
            object: Результат выполнения запроса.
        """
        _ = execution_options, bind_arguments, kwargs
        return await self._session.execute(statement, params=params)
