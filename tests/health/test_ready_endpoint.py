from __future__ import annotations

import json
from collections.abc import Mapping
from typing import Any

import pytest
from fastapi.responses import JSONResponse

from pybot.dto.health_dto import HealthStatusDTO
from pybot.health.app import ready
from pybot.services.health import HealthService, SupportsExecute


class _FakeSession(SupportsExecute):
    def __init__(self, should_fail: bool, error: Exception | None = None) -> None:
        self._should_fail = should_fail
        self._error = error or RuntimeError("database is not reachable")

    async def execute(
        self,
        statement: Any,
        params: Mapping[str, object] | None = None,
        *,
        execution_options: Mapping[str, object] | None = None,
        bind_arguments: Mapping[str, object] | None = None,
        **kwargs: object,
    ) -> object:
        if self._should_fail:
            raise self._error
        return object()


@pytest.mark.asyncio
async def test_health_service_ready_ok_reports_database_check() -> None:
    """Говорящий тест: when DB is reachable, readiness should be OK and include a DB check."""
    service = HealthService(_FakeSession(should_fail=False))

    status, is_ready = await service.ready()

    assert is_ready is True, "Ready must be True when DB is reachable."
    assert status.status == "ok", "Overall status should be ok for successful DB check."
    assert status.checks, "Readiness should report at least one check."
    assert status.checks[0].name == "database", "First check should describe the DB."
    assert status.checks[0].status == "ok", "DB check should be ok when DB is reachable."


@pytest.mark.asyncio
async def test_health_service_ready_fail_is_descriptive() -> None:
    """Empathetic test: when DB is down, readiness must be fail with a useful detail."""
    error = RuntimeError("db down")
    service = HealthService(_FakeSession(should_fail=True, error=error))

    status, is_ready = await service.ready()

    assert is_ready is False, "Ready must be False when DB is not reachable."
    assert status.status == "fail", "Overall status should be fail when DB check fails."
    assert status.checks[0].status == "fail", "DB check should be marked as fail."
    assert "db down" in (status.checks[0].details or ""), "Failure should explain why DB is down."


@pytest.mark.asyncio
async def test_ready_endpoint_returns_200_on_ok() -> None:
    """Friendly test: /ready should return DTO directly when ready."""
    service = HealthService(_FakeSession(should_fail=False))
    response = await ready(service)

    assert isinstance(response, HealthStatusDTO), "Expected DTO response when service is ready."
    assert response.status == "ok", "DTO should carry ok status."


@pytest.mark.asyncio
async def test_ready_endpoint_returns_503_on_fail() -> None:
    """Friendly test: /ready should return 503 with details when DB is down."""
    service = HealthService(_FakeSession(should_fail=True, error=RuntimeError("db down")))
    response = await ready(service)

    assert isinstance(response, JSONResponse), "Expected JSONResponse when service is not ready."
    assert response.status_code == 503, "HTTP status must be 503 for readiness failure."

    payload = json.loads(bytes(response.body).decode("utf-8"))
    assert payload["status"] == "fail", "Payload should report fail status."
    assert payload["checks"][0]["details"] == "db down", "Payload should include failure details."
