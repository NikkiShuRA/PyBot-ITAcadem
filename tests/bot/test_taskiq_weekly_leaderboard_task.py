from __future__ import annotations

from collections.abc import Awaitable
from typing import Protocol, cast

import pytest
from taskiq.brokers.inmemory_broker import InMemoryBroker

from pybot.core.config import BotSettings
from pybot.infrastructure.taskiq.tasks.leaderboard import publish_weekly_leaderboard_task, register_tasks
from pybot.services.weekly_leaderboard_publisher import WeeklyLeaderboardPublisherService


class WeeklyPublisherServiceSpy(WeeklyLeaderboardPublisherService):
    def __init__(self) -> None:
        self.calls: list[tuple[int, int, str]] = []

    async def publish_weekly(self, *, recipient_id: int, limit: int, business_tz: str) -> None:
        self.calls.append((recipient_id, limit, business_tz))


class DishkaContainer(Protocol):
    async def get(
        self,
        dependency_type: type[object],
        *args: object,
        component: str | None = None,
        **kwargs: object,
    ) -> object: ...


class TaskCallable(Protocol):
    def __call__(
        self,
        *,
        recipient_id: int,
        limit: int,
        dishka_container: DishkaContainer,
    ) -> Awaitable[dict[str, int]]: ...


class DishkaContainerStub:
    def __init__(self, service: WeeklyLeaderboardPublisherService, settings_obj: BotSettings) -> None:
        self._service = service
        self._settings = settings_obj

    async def get(
        self,
        dependency_type: type[object],
        *args: object,
        component: str | None = None,
        **kwargs: object,
    ) -> object:
        resolved_component = component
        if args:
            resolved_component = args[0]
        elif "component" in kwargs:
            resolved_component = kwargs["component"]

        assert resolved_component in ("", None)
        if dependency_type is WeeklyLeaderboardPublisherService:
            return self._service
        if dependency_type is BotSettings:
            return self._settings
        raise AssertionError(f"Unexpected dependency requested: {dependency_type}")


def _build_registered_task(settings_obj: BotSettings) -> TaskCallable:
    broker = InMemoryBroker()
    task = register_tasks(broker=broker, settings=settings_obj)
    return cast(TaskCallable, task)


@pytest.mark.asyncio
async def test_publish_weekly_leaderboard_task_uses_service_and_returns_payload(settings_obj: BotSettings) -> None:
    service = WeeklyPublisherServiceSpy()
    task = _build_registered_task(settings_obj)
    dishka_container = DishkaContainerStub(service, settings_obj)

    payload = await task(
        recipient_id=-100_200_300,
        limit=12,
        dishka_container=dishka_container,
    )

    assert payload == {
        "recipient_id": -100_200_300,
        "limit": 12,
    }
    assert service.calls == [(-100_200_300, 12, str(settings_obj.leaderboard_weekly_timezone))]


def test_publish_weekly_leaderboard_task_has_retry_labels(settings_obj: BotSettings) -> None:
    task = register_tasks(broker=InMemoryBroker(), settings=settings_obj)

    assert task.task_name == "leaderboard.publish_weekly"
    assert task.labels["retry_on_error"] == settings_obj.leaderboard_weekly_retry_enabled
    assert task.labels["max_retries"] == settings_obj.leaderboard_weekly_retry_max_retries
    assert task.labels["delay"] == settings_obj.leaderboard_weekly_retry_delay_s
    assert callable(publish_weekly_leaderboard_task)
