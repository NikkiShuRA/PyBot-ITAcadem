from __future__ import annotations

from datetime import UTC, datetime
from types import SimpleNamespace

import pytest
from dishka import Provider, Scope, make_async_container, provide
from fastapi import FastAPI
from fastapi.testclient import TestClient

from pybot.dto.health_dto import HealthCheckDTO, HealthStatusDTO
from pybot.presentation import web as web_presentation
from pybot.services.health import HealthService


class StubHealthService(HealthService):
    """Deterministic health service stub for app-level HTTP smoke tests."""

    def __init__(self, is_ready: bool) -> None:
        self._is_ready = is_ready

    async def health(self) -> HealthStatusDTO:
        return HealthStatusDTO(
            status="ok",
            checks=[],
            timestamp=datetime.now(UTC),
        )

    async def ready(self) -> tuple[HealthStatusDTO, bool]:
        check_status = "ok" if self._is_ready else "fail"
        status = "ok" if self._is_ready else "fail"
        details = None if self._is_ready else "database is down"
        return (
            HealthStatusDTO(
                status=status,
                checks=[
                    HealthCheckDTO(
                        name="database",
                        status=check_status,
                        details=details,
                        latency_ms=1,
                    ),
                    HealthCheckDTO(
                        name="redis",
                        status=check_status,
                        details=details if not self._is_ready else None,
                        latency_ms=1,
                    ),
                ],
                timestamp=datetime.now(UTC),
            ),
            self._is_ready,
        )


class StubHealthProvider(Provider):
    """Dishka provider that injects a predefined health service stub."""

    def __init__(self, service: HealthService) -> None:
        super().__init__()
        self._service = service

    @provide(scope=Scope.REQUEST)
    def health_service(self) -> HealthService:
        return self._service


def create_test_app(
    monkeypatch: pytest.MonkeyPatch,
    service: HealthService,
) -> FastAPI:
    """Build FastAPI app with patched health container for integration-like tests."""
    container = make_async_container(StubHealthProvider(service))
    monkeypatch.setattr(web_presentation.main, "setup_health_container", lambda: container)
    return web_presentation.create_app()


@pytest.mark.asyncio
async def test_lifespan_logs_start_stop_and_closes_dishka_container(
    monkeypatch: pytest.MonkeyPatch,
    mocker,
) -> None:
    """Verify lifespan logs startup/shutdown and closes existing dishka container."""
    info_spy = mocker.Mock()
    close_spy = mocker.AsyncMock()
    app = FastAPI()
    app.state.dishka_container = SimpleNamespace(close=close_spy)
    monkeypatch.setattr(web_presentation.main.logger, "info", info_spy)

    async with web_presentation.lifespan(app):
        pass

    close_spy.assert_awaited_once()
    assert info_spy.call_args_list == [
        mocker.call("Health API started"),
        mocker.call("Health API stopped"),
    ]


@pytest.mark.asyncio
async def test_lifespan_does_not_fail_when_dishka_container_is_missing(
    monkeypatch: pytest.MonkeyPatch,
    mocker,
) -> None:
    """Ensure shutdown path is resilient when app state has no dishka container."""
    info_spy = mocker.Mock()
    app = FastAPI()
    monkeypatch.setattr(web_presentation.main.logger, "info", info_spy)

    async with web_presentation.lifespan(app):
        pass

    assert info_spy.call_args_list == [
        mocker.call("Health API started"),
        mocker.call("Health API stopped"),
    ]


def test_create_app_health_endpoint_smoke(monkeypatch: pytest.MonkeyPatch) -> None:
    """Smoke-check GET /health through create_app + TestClient."""
    app = create_test_app(monkeypatch, StubHealthService(is_ready=True))

    with TestClient(app) as client:
        response = client.get("/health")

    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "ok"
    assert payload["checks"] == []
    assert "timestamp" in payload


@pytest.mark.parametrize(
    ("is_ready", "expected_status_code", "expected_status"),
    [
        (True, 200, "ok"),
        (False, 503, "fail"),
    ],
)
def test_create_app_ready_endpoint_smoke(
    monkeypatch: pytest.MonkeyPatch,
    is_ready: bool,
    expected_status_code: int,
    expected_status: str,
) -> None:
    """Smoke-check GET /ready returning 200/503 depending on injected service behavior."""
    app = create_test_app(monkeypatch, StubHealthService(is_ready=is_ready))

    with TestClient(app) as client:
        response = client.get("/ready")

    assert response.status_code == expected_status_code
    payload = response.json()
    assert payload["status"] == expected_status
    assert [check["name"] for check in payload["checks"]] == ["database", "redis"]
