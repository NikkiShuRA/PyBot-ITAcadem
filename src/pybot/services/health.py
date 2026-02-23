from __future__ import annotations

import time
from collections.abc import Mapping
from datetime import UTC, datetime
from typing import Protocol

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql.base import Executable

from ..dto.health_dto import HealthCheckDTO, HealthStatusDTO


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


class SessionExecutor(SupportsExecute):
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
        # Health checks only need a minimal "SELECT 1"; extra options are ignored.
        _ = execution_options, bind_arguments, kwargs
        return await self._session.execute(statement, params=params)


class HealthService:
    def __init__(self, db: SupportsExecute) -> None:
        self._db = db

    async def health(self) -> HealthStatusDTO:
        return HealthStatusDTO(
            status="ok",
            checks=[],
            timestamp=datetime.now(UTC),
        )

    async def ready(self) -> tuple[HealthStatusDTO, bool]:
        start = time.perf_counter()
        try:
            await self._db.execute(text("SELECT 1"))
            latency_ms = int((time.perf_counter() - start) * 1000)
            check = HealthCheckDTO(
                name="database",
                status="ok",
                latency_ms=latency_ms,
            )
            status = HealthStatusDTO(
                status="ok",
                checks=[check],
                timestamp=datetime.now(UTC),
            )
        except Exception as exc:
            latency_ms = int((time.perf_counter() - start) * 1000)
            check = HealthCheckDTO(
                name="database",
                status="fail",
                details=str(exc),
                latency_ms=latency_ms,
            )
            status = HealthStatusDTO(
                status="fail",
                checks=[check],
                timestamp=datetime.now(UTC),
            )
            return status, False
        else:
            return status, True
