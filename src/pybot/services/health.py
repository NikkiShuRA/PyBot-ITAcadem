from __future__ import annotations

import time
from datetime import UTC, datetime

from sqlalchemy import text

from ..core import logger
from ..dto.health_dto import HealthCheckDTO, HealthStatusDTO
from .ports.health_probe import SupportsExecute, SupportsPing


class HealthService:
    def __init__(self, db: SupportsExecute, redis_probe: SupportsPing) -> None:
        self._db = db
        self._redis_probe = redis_probe

    async def health(self) -> HealthStatusDTO:
        return HealthStatusDTO(
            status="ok",
            checks=[],
            timestamp=datetime.now(UTC),
        )

    async def _check_database(self) -> HealthCheckDTO:
        start = time.perf_counter()
        try:
            await self._db.execute(text("SELECT 1"))
        except Exception as err:
            latency_ms = int((time.perf_counter() - start) * 1000)
            logger.exception("Database readiness check failed")
            return HealthCheckDTO(
                name="database",
                status="fail",
                details=str(err),
                latency_ms=latency_ms,
            )

        latency_ms = int((time.perf_counter() - start) * 1000)
        return HealthCheckDTO(
            name="database",
            status="ok",
            latency_ms=latency_ms,
        )

    async def _check_redis(self) -> HealthCheckDTO:
        start = time.perf_counter()
        try:
            await self._redis_probe.ping()
        except Exception as err:
            latency_ms = int((time.perf_counter() - start) * 1000)
            logger.exception("Redis readiness check failed")
            return HealthCheckDTO(
                name="redis",
                status="fail",
                details=str(err),
                latency_ms=latency_ms,
            )

        latency_ms = int((time.perf_counter() - start) * 1000)
        return HealthCheckDTO(
            name="redis",
            status="ok",
            latency_ms=latency_ms,
        )

    async def ready(self) -> tuple[HealthStatusDTO, bool]:
        checks = [
            await self._check_database(),
            await self._check_redis(),
        ]
        is_ready = all(check.status == "ok" for check in checks)
        status = HealthStatusDTO(
            status="ok" if is_ready else "fail",
            checks=checks,
            timestamp=datetime.now(UTC),
        )
        return status, is_ready
