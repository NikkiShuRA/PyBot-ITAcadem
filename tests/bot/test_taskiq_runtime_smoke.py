from __future__ import annotations

from collections.abc import Iterator
import importlib
import sys
from types import SimpleNamespace
from typing import Any, cast
from unittest.mock import AsyncMock, Mock

import pytest

from pybot.infrastructure.taskiq import taskiq_app
from pybot.infrastructure.taskiq.tasks.system import system_ping_task


@pytest.fixture(autouse=True)
def reset_taskiq_runtime_state() -> Iterator[None]:
    """Keep TaskIQ singleton state isolated so smoke failures stay easy to read."""
    taskiq_app._runtime_state.broker = None
    taskiq_app._runtime_state.scheduler = None
    taskiq_app._runtime_state.schedule_source = None
    taskiq_app._runtime_state.container = None
    yield
    taskiq_app._runtime_state.broker = None
    taskiq_app._runtime_state.scheduler = None
    taskiq_app._runtime_state.schedule_source = None
    taskiq_app._runtime_state.container = None


@pytest.mark.asyncio
async def test_taskiq_runtime_smoke_builds_singletons_and_wires_worker_hooks(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Smoke test for TaskIQ runtime wiring with a friendly failure signal."""

    class FakeBroker:
        def __init__(self, url: str) -> None:
            self.url = url
            self.handlers: list[tuple[object, object]] = []

        def add_event_handler(self, event: object, handler: object) -> None:
            self.handlers.append((event, handler))

    class FakeScheduleSource:
        def __init__(self, url: str) -> None:
            self.url = url

    class FakeScheduler:
        def __init__(self, broker: FakeBroker, sources: list[FakeScheduleSource]) -> None:
            self.broker = broker
            self.sources = sources

    monkeypatch.setattr(taskiq_app.settings, "redis_url", "redis://smoke-test:6379/7")
    monkeypatch.setattr(taskiq_app, "RedisStreamBroker", FakeBroker)
    monkeypatch.setattr(taskiq_app, "ListRedisScheduleSource", FakeScheduleSource)
    monkeypatch.setattr(taskiq_app, "TaskiqScheduler", FakeScheduler)

    broker = cast(FakeBroker, taskiq_app.get_taskiq_broker())
    second_broker = cast(FakeBroker, taskiq_app.get_taskiq_broker())
    source = cast(FakeScheduleSource, taskiq_app.get_taskiq_schedule_source())
    second_source = cast(FakeScheduleSource, taskiq_app.get_taskiq_schedule_source())
    scheduler = cast(FakeScheduler, taskiq_app.get_taskiq_scheduler())
    second_scheduler = cast(FakeScheduler, taskiq_app.get_taskiq_scheduler())

    assert broker is second_broker, "TaskIQ broker singleton drifted. Smoke check expected one shared broker instance."
    assert source is second_source, "TaskIQ schedule source should stay singleton so delayed jobs use one Redis source."
    assert (
        scheduler is second_scheduler
    ), "TaskIQ scheduler singleton changed unexpectedly. Please re-check runtime wiring."
    assert broker.url == "redis://smoke-test:6379/7"
    assert source.url == "redis://smoke-test:6379/7"
    assert scheduler.broker is broker
    assert scheduler.sources == [source]
    assert broker.handlers == [
        (taskiq_app.TaskiqEvents.WORKER_STARTUP, taskiq_app._on_worker_startup),
        (taskiq_app.TaskiqEvents.WORKER_SHUTDOWN, taskiq_app._on_worker_shutdown),
    ], "Worker lifecycle hooks were not attached. Startup and shutdown diagnostics would become misleading."


@pytest.mark.asyncio
async def test_taskiq_worker_lifecycle_smoke_initializes_and_closes_dishka_container(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Smoke test for worker lifecycle so DI bootstrap failures are easier to spot."""

    fake_broker = SimpleNamespace()
    fake_container = SimpleNamespace(close=AsyncMock())
    setup_container = Mock(return_value=fake_container)
    setup_dishka = Mock()

    taskiq_app._runtime_state.broker = cast(Any, fake_broker)
    monkeypatch.setattr(taskiq_app, "setup_taskiq_container", setup_container)
    monkeypatch.setattr(taskiq_app, "setup_dishka", setup_dishka)

    await taskiq_app._on_worker_startup(cast(Any, SimpleNamespace()))

    assert (
        taskiq_app._runtime_state.container is fake_container
    ), "Worker startup did not keep the Dishka container alive. Background tasks would lose their dependencies."
    setup_container.assert_called_once_with()
    setup_dishka.assert_called_once_with(container=fake_container, broker=fake_broker)

    await taskiq_app._on_worker_shutdown(cast(Any, SimpleNamespace()))

    fake_container.close.assert_awaited_once()
    assert (
        taskiq_app._runtime_state.container is None
    ), "Worker shutdown left the DI container hanging around. That usually points to an incomplete cleanup path."


@pytest.mark.asyncio
async def test_system_ping_task_smoke_returns_pong() -> None:
    """Tiny smoke test so there is always a friendly canary task for manual checks."""
    result = await system_ping_task()

    assert result == "pong", "The TaskIQ canary task stopped replying with 'pong'. Start from the worker wiring first."


def test_taskiq_entrypoint_smoke_exposes_broker_scheduler_and_registers_tasks(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Smoke test for the public TaskIQ entrypoint used by worker and scheduler CLI."""
    fake_broker = object()
    fake_scheduler = object()
    imported_specs: list[str] = []

    def fake_import_module(name: str, package: str | None = None) -> object:
        imported_specs.append(name if package is None else f"{package}:{name}")
        return SimpleNamespace()

    monkeypatch.setattr(taskiq_app, "get_taskiq_broker", lambda: fake_broker)
    monkeypatch.setattr(taskiq_app, "get_taskiq_scheduler", lambda: fake_scheduler)
    monkeypatch.setattr(importlib, "import_module", fake_import_module)

    sys.modules.pop("pybot.infrastructure.taskiq.entrypoint", None)
    entrypoint = __import__("pybot.infrastructure.taskiq.entrypoint", fromlist=["broker", "scheduler"])

    assert (
        entrypoint.broker is fake_broker
    ), "Public TaskIQ entrypoint lost the broker handle. `taskiq worker ...:broker` would stop seeing the runtime."
    assert (
        entrypoint.scheduler is fake_scheduler
    ), "Public TaskIQ entrypoint lost the scheduler handle. `taskiq scheduler ...:scheduler` would stop booting."
    assert (
        imported_specs == ["pybot.infrastructure.taskiq.tasks"]
    ), "Entrypoint did not register the tasks package on import. Worker startup would look healthy but no tasks would exist."
