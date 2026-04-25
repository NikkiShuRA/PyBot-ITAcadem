from __future__ import annotations

from collections.abc import Mapping
from typing import Protocol

from sqlalchemy.sql.base import Executable


class SupportsExecute(Protocol):
    """Протокол для объектов, поддерживающих выполнение SQL-запросов.

    Используется для абстрагирования от конкретной реализации сессии БД
    при проверке liveness/readiness.
    """

    async def execute(
        self,
        statement: Executable,
        params: Mapping[str, object] | None = None,
        *,
        execution_options: Mapping[str, object] | None = None,
        bind_arguments: Mapping[str, object] | None = None,
        **kwargs: object,
    ) -> object:
        """Выполняет переданный SQL-запрос.

        Args:
            statement: Исполняемое выражение.
            params: Параметры запроса.
            execution_options: Опции выполнения.
            bind_arguments: Аргументы привязки.
            **kwargs: Дополнительные параметры.

        Returns:
            object: Результат выполнения запроса.
        """
        ...


class SupportsPing(Protocol):
    """Протокол для объектов, поддерживающих команду ping (например, Redis)."""

    async def ping(self) -> object:
        """Выполняет проверку доступности (ping).

        Returns:
            object: Результат команды ping.
        """
        ...
