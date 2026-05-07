from __future__ import annotations

from collections.abc import Awaitable
from typing import Protocol, cast
from unittest.mock import AsyncMock

import pytest
from pydantic import ValidationError
from taskiq.brokers.inmemory_broker import InMemoryBroker

from pybot.dto import NotificationTaskPayload, NotifyDTO
from pybot.infrastructure.taskiq.tasks.notification import register_tasks, send_notification_task
from pybot.services.ports import NotificationPermanentError, NotificationPort, NotificationTemporaryError


class NotificationPortSpy(NotificationPort):
    def __init__(self, send_message_mock: AsyncMock) -> None:
        self.send_message_mock = send_message_mock

    async def send_role_request_to_admin(
        self,
        request_id: int,
        requester_user_id: int,
        role_name: str,
    ) -> None:
        return None

    async def send_message(self, message_data: NotifyDTO) -> None:
        await self.send_message_mock(message_data)


class DishkaContainer(Protocol):
    async def get(
        self,
        dependency_type: type[NotificationPort],
        *args: object,
        component: str | None = None,
        **kwargs: object,
    ) -> NotificationPort: ...


class TaskCallable(Protocol):
    def __call__(
        self,
        *,
        notification_data: NotifyDTO,
        dishka_container: DishkaContainer,
    ) -> Awaitable[NotificationTaskPayload]: ...


class DishkaContainerStub:
    def __init__(self, notification_port: NotificationPort) -> None:
        self._notification_port = notification_port

    async def get(
        self,
        dependency_type: type[NotificationPort],
        *args: object,
        component: str | None = None,
        **kwargs: object,
    ) -> NotificationPort:
        assert dependency_type is NotificationPort
        resolved_component = component
        if args:
            resolved_component = args[0]
        elif "component" in kwargs:
            resolved_component = kwargs["component"]

        assert resolved_component in ("", None)
        return self._notification_port


def _build_task() -> TaskCallable:
    broker = InMemoryBroker()
    task = register_tasks(broker=broker)
    return cast(TaskCallable, task)


async def _run_task(notification_port: NotificationPort, notification_data: NotifyDTO) -> NotificationTaskPayload:
    dishka_container = DishkaContainerStub(notification_port)
    task = _build_task()
    task_call = task(notification_data=notification_data, dishka_container=dishka_container)
    assert isinstance(task_call, Awaitable)
    return await task_call


@pytest.mark.asyncio
async def test_send_notification_task_smoke_sends_trimmed_message() -> None:
    notification_port = NotificationPortSpy(AsyncMock())

    result = await _run_task(notification_port, NotifyDTO(recipient_id=111, message="  hello world  "))

    assert result.status == "sent", (
        "Notification task stopped reporting successful delivery. Start from payload validation."
    )
    assert result.message == "hello world"
    notification_port.send_message_mock.assert_awaited_once_with(NotifyDTO(recipient_id=111, message="hello world"))


@pytest.mark.asyncio
async def test_send_notification_task_returns_temporary_failure_payload() -> None:
    notification_port = NotificationPortSpy(
        AsyncMock(side_effect=NotificationTemporaryError("network wobble", retry_after_seconds=1.0))
    )

    result = await _run_task(notification_port, NotifyDTO(recipient_id=222, message="hello world"))

    assert result.status == "failed_temporary"
    assert result.recipient_id == 222


@pytest.mark.asyncio
async def test_send_notification_task_returns_permanent_failure_payload() -> None:
    notification_port = NotificationPortSpy(AsyncMock(side_effect=NotificationPermanentError("blocked")))

    result = await _run_task(notification_port, NotifyDTO(recipient_id=333, message="hello world"))

    assert result.status == "failed_permanent"
    assert result.message == "hello world"


def test_notify_dto_rejects_blank_message_before_task_execution() -> None:
    with pytest.raises(ValidationError, match="message must not be empty"):
        NotifyDTO(recipient_id=444, message="   ")


def test_notify_dto_rejects_zero_recipient_id_before_task_execution() -> None:
    with pytest.raises(ValidationError, match="equal to 0"):
        NotifyDTO(recipient_id=0, message="hello")


@pytest.mark.asyncio
async def test_send_notification_task_preserves_parse_mode() -> None:
    notification_port = NotificationPortSpy(AsyncMock())

    await _run_task(
        notification_port,
        NotifyDTO(recipient_id=555, message="<b>hello</b>", parse_mode="HTML"),
    )

    notification_port.send_message_mock.assert_awaited_once_with(
        NotifyDTO(recipient_id=555, message="<b>hello</b>", parse_mode="HTML")
    )
    assert callable(send_notification_task)
