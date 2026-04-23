from __future__ import annotations

from collections.abc import Mapping
from typing import Protocol

from sqlalchemy.sql.base import Executable


class SupportsExecute(Protocol):
    async def execute(
        self,
        statement: Executable,
        params: Mapping[str, object] | None = None,
        *,
        execution_options: Mapping[str, object] | None = None,
        bind_arguments: Mapping[str, object] | None = None,
        **kwargs: object,
    ) -> object: ...


class SupportsPing(Protocol):
    async def ping(self) -> object: ...
