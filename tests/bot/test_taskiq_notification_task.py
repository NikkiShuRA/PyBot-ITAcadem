from __future__ import annotations

from types import SimpleNamespace
from typing import Any, cast
from unittest.mock import AsyncMock

import pytest
from dishka.integrations.taskiq import CONTAINER_NAME

from pybot.infrastructure.taskiq.tasks.notification import send_notification_task
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

    async def send_message(self, user_id: int, message_text: str) -> None:
        await self.send_message_mock(user_id=user_id, message_text=message_text)


def _task() -> Any:
    return cast(Any, send_notification_task)


@pytest.mark.asyncio
async def test_send_notification_task_smoke_sends_trimmed_message() -> None:
    notification_port = NotificationPortSpy(AsyncMock())
    dishka_container = SimpleNamespace(get=AsyncMock(return_value=notification_port))

    result = await _task()(
        user_id=111,
        message="  hello world  ",
        **{CONTAINER_NAME: dishka_container},
    )

    assert (
        result.status == "sent"
    ), "Notification task stopped reporting successful delivery. Start from payload validation."
    assert result.message == "hello world"
    notification_port.send_message_mock.assert_awaited_once_with(user_id=111, message_text="hello world")


@pytest.mark.asyncio
async def test_send_notification_task_returns_temporary_failure_payload() -> None:
    notification_port = NotificationPortSpy(
        AsyncMock(side_effect=NotificationTemporaryError("network wobble", retry_after_seconds=1.0))
    )
    dishka_container = SimpleNamespace(get=AsyncMock(return_value=notification_port))

    result = await _task()(
        user_id=222,
        message="hello world",
        **{CONTAINER_NAME: dishka_container},
    )

    assert result.status == "failed_temporary"
    assert result.user_id == 222


@pytest.mark.asyncio
async def test_send_notification_task_returns_permanent_failure_payload() -> None:
    notification_port = NotificationPortSpy(AsyncMock(side_effect=NotificationPermanentError("blocked")))
    dishka_container = SimpleNamespace(get=AsyncMock(return_value=notification_port))

    result = await _task()(
        user_id=333,
        message="hello world",
        **{CONTAINER_NAME: dishka_container},
    )

    assert result.status == "failed_permanent"
    assert result.message == "hello world"


@pytest.mark.asyncio
async def test_send_notification_task_rejects_blank_message_before_delivery_attempt() -> None:
    notification_port = NotificationPortSpy(AsyncMock())
    dishka_container = SimpleNamespace(get=AsyncMock(return_value=notification_port))

    with pytest.raises(ValueError, match="Message cannot be empty"):
        await _task()(
            user_id=444,
            message="   ",
            **{CONTAINER_NAME: dishka_container},
        )

    notification_port.send_message_mock.assert_not_awaited()
