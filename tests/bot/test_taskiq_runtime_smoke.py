from __future__ import annotations

from collections.abc import Iterator
import sys
from types import SimpleNamespace
from typing import Any, cast
from unittest.mock import AsyncMock, Mock

import pytest

from pybot.core.config import BotSettings
from pybot.infrastructure.taskiq import taskiq_app
from pybot.infrastructure.taskiq import taskiq_weekly_leaderboard_wiring
from pybot.infrastructure.taskiq.tasks import TaskRegistry
from pybot.infrastructure.taskiq.tasks.system import system_ping_task
from pybot.services.ports import NotificationTemporaryError


@pytest.fixture(autouse=True)
def reset_taskiq_runtime_state() -> Iterator[None]:
    """Keep TaskIQ singleton state isolated so smoke failures stay easy to read."""
    taskiq_app._runtime_state.broker = None
    taskiq_app._runtime_state.scheduler = None
    taskiq_app._runtime_state.schedule_source = None
    taskiq_app._runtime_state.container = None
    taskiq_app._runtime_state.task_registry = None
    yield
    taskiq_app._runtime_state.broker = None
    taskiq_app._runtime_state.scheduler = None
    taskiq_app._runtime_state.schedule_source = None
    taskiq_app._runtime_state.container = None
    taskiq_app._runtime_state.task_registry = None


@pytest.mark.asyncio
async def test_taskiq_runtime_smoke_builds_singletons_and_wires_worker_hooks(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Smoke test for TaskIQ runtime wiring with a friendly failure signal."""

    class FakeBroker:
        def __init__(self, url: str) -> None:
            self.url = url
            self.handlers: list[tuple[object, object]] = []
            self.middlewares: list[object] = []

        def add_event_handler(self, event: object, handler: object) -> None:
            self.handlers.append((event, handler))

        def add_middlewares(self, *middlewares: object) -> None:
            self.middlewares.extend(middlewares)

    class FakeScheduleSource:
        def __init__(self, url: str) -> None:
            self.url = url

    class FakeScheduler:
        def __init__(self, broker: FakeBroker, sources: list[FakeScheduleSource]) -> None:
            self.broker = broker
            self.sources = sources

    class FakeSmartRetryMiddleware:
        def __init__(
            self,
            *,
            default_retry_count: int,
            default_retry_label: bool,
            default_delay: float,
            use_jitter: bool,
            use_delay_exponent: bool,
            max_delay_exponent: float,
            schedule_source: object,
            types_of_exceptions: tuple[type[BaseException], ...],
        ) -> None:
            self.default_retry_count = default_retry_count
            self.default_retry_label = default_retry_label
            self.default_delay = default_delay
            self.use_jitter = use_jitter
            self.use_delay_exponent = use_delay_exponent
            self.max_delay_exponent = max_delay_exponent
            self.schedule_source = schedule_source
            self.types_of_exceptions = types_of_exceptions

    runtime_settings = cast(
        BotSettings,
        SimpleNamespace(
            redis_url="redis://smoke-test:6379/7",
            leaderboard_weekly_retry_max_retries=4,
            leaderboard_weekly_retry_delay_s=42,
            leaderboard_weekly_retry_use_jitter=False,
            leaderboard_weekly_retry_use_exponential_backoff=True,
            leaderboard_weekly_retry_max_delay_s=512,
        ),
    )
    fake_registry = TaskRegistry(
        broadcast_task=cast(Any, SimpleNamespace(task_name="broadcast.send_for_all")),
        notification_task=cast(
            Any,
            SimpleNamespace(
                task_name="notification.send_notification_task",
                kicker=lambda: SimpleNamespace(),
            ),
        ),
        system_task=cast(Any, SimpleNamespace(task_name="system.ping")),
        weekly_leaderboard_task=cast(
            Any,
            SimpleNamespace(task_name="leaderboard.publish_weekly", kicker=lambda: SimpleNamespace()),
        ),
    )
    register_all_tasks = Mock(return_value=fake_registry)

    monkeypatch.setattr(taskiq_app, "register_all_tasks", register_all_tasks)
    monkeypatch.setattr(taskiq_app, "RedisStreamBroker", FakeBroker)
    monkeypatch.setattr(taskiq_app, "ListRedisScheduleSource", FakeScheduleSource)
    monkeypatch.setattr(taskiq_app, "TaskiqScheduler", FakeScheduler)
    monkeypatch.setattr(taskiq_app, "SmartRetryMiddleware", FakeSmartRetryMiddleware)

    broker = cast(FakeBroker, taskiq_app.get_taskiq_broker(runtime_settings))
    second_broker = cast(FakeBroker, taskiq_app.get_taskiq_broker(runtime_settings))
    source = cast(FakeScheduleSource, taskiq_app.get_taskiq_schedule_source(runtime_settings))
    second_source = cast(FakeScheduleSource, taskiq_app.get_taskiq_schedule_source(runtime_settings))
    scheduler = cast(FakeScheduler, taskiq_app.get_taskiq_scheduler(runtime_settings))
    second_scheduler = cast(FakeScheduler, taskiq_app.get_taskiq_scheduler(runtime_settings))

    assert broker is second_broker, "TaskIQ broker singleton drifted. Smoke check expected one shared broker instance."
    assert source is second_source, "TaskIQ schedule source should stay singleton so delayed jobs use one Redis source."
    assert scheduler is second_scheduler, (
        "TaskIQ scheduler singleton changed unexpectedly. Please re-check runtime wiring."
    )
    assert broker.url == "redis://smoke-test:6379/7"
    assert source.url == "redis://smoke-test:6379/7"
    assert scheduler.broker is broker
    assert scheduler.sources == [source]
    assert len(broker.middlewares) == 1
    retry_middleware = broker.middlewares[0]
    assert isinstance(retry_middleware, FakeSmartRetryMiddleware)
    assert retry_middleware.default_retry_count == 4
    assert retry_middleware.default_retry_label is False
    assert retry_middleware.default_delay == 42.0
    assert retry_middleware.use_jitter is False
    assert retry_middleware.use_delay_exponent is True
    assert retry_middleware.max_delay_exponent == 512.0
    assert retry_middleware.schedule_source is source
    assert retry_middleware.types_of_exceptions == (NotificationTemporaryError,)
    assert broker.handlers == [
        (taskiq_app.TaskiqEvents.WORKER_STARTUP, taskiq_app._on_worker_startup),
        (taskiq_app.TaskiqEvents.WORKER_SHUTDOWN, taskiq_app._on_worker_shutdown),
        (taskiq_app.TaskiqEvents.CLIENT_STARTUP, taskiq_weekly_leaderboard_wiring._on_client_startup_weekly),
    ], "Worker lifecycle hooks were not attached. Startup and shutdown diagnostics would become misleading."
    register_all_tasks.assert_called_once_with(broker=broker, settings=runtime_settings)
    assert taskiq_app.get_taskiq_task_registry(runtime_settings) is fake_registry
    assert taskiq_app.get_taskiq_notification_task(runtime_settings) is fake_registry.notification_task
    assert taskiq_app.get_taskiq_weekly_leaderboard_task(runtime_settings) is fake_registry.weekly_leaderboard_task


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

    assert taskiq_app._runtime_state.container is fake_container, (
        "Worker startup did not keep the Dishka container alive. Background tasks would lose their dependencies."
    )
    setup_container.assert_called_once_with()
    setup_dishka.assert_called_once_with(container=fake_container, broker=fake_broker)

    await taskiq_app._on_worker_shutdown(cast(Any, SimpleNamespace()))

    fake_container.close.assert_awaited_once()
    assert taskiq_app._runtime_state.container is None, (
        "Worker shutdown left the DI container hanging around. That usually points to an incomplete cleanup path."
    )


@pytest.mark.asyncio
async def test_system_ping_task_smoke_returns_pong() -> None:
    """Tiny smoke test so there is always a friendly canary task for manual checks."""
    result = await system_ping_task()

    assert result == "pong", "The TaskIQ canary task stopped replying with 'pong'. Start from the worker wiring first."


def test_taskiq_entrypoint_smoke_exposes_broker_and_scheduler(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Smoke test for the public TaskIQ entrypoint used by worker and scheduler CLI."""
    fake_broker = object()
    fake_scheduler = object()
    get_broker = Mock(return_value=fake_broker)
    get_scheduler = Mock(return_value=fake_scheduler)

    monkeypatch.setattr(taskiq_app, "get_taskiq_broker", get_broker)
    monkeypatch.setattr(taskiq_app, "get_taskiq_scheduler", get_scheduler)

    sys.modules.pop("pybot.infrastructure.taskiq.entrypoint", None)
    entrypoint = __import__("pybot.infrastructure.taskiq.entrypoint", fromlist=["broker", "scheduler"])

    assert entrypoint.broker is fake_broker, (
        "Public TaskIQ entrypoint lost the broker handle. `taskiq worker ...:broker` would stop seeing the runtime."
    )
    assert entrypoint.scheduler is fake_scheduler, (
        "Public TaskIQ entrypoint lost the scheduler handle. `taskiq scheduler ...:scheduler` would stop booting."
    )
    get_broker.assert_called_once_with()
    get_scheduler.assert_called_once_with()
