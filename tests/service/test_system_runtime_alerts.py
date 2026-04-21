import pytest

from pybot.core.config import settings
from pybot.core.constants import TaskScheduleKind
from pybot.dto import NotifyDTO
from pybot.services.notification_facade import NotificationFacade
from pybot.services.ports import NotificationPort
from pybot.services.system_runtime_alerts import SystemRuntimeAlertsService


class NotificationFacadeSpy(NotificationFacade):
    def __init__(self) -> None:
        self.calls = []

    async def notify_user(self, data) -> None:
        self.calls.append(data)


class NotificationPortSpy(NotificationPort):
    def __init__(self) -> None:
        self.message_calls: list[NotifyDTO] = []

    async def send_role_request_to_admin(
        self,
        request_id: int,
        requester_user_id: int,
        role_name: str,
    ) -> None:
        return None

    async def send_message(self, message_data: NotifyDTO) -> None:
        self.message_calls.append(message_data)


@pytest.mark.asyncio
async def test_runtime_alerts_service_skips_when_alerts_are_disabled(monkeypatch: pytest.MonkeyPatch) -> None:
    startup_facade = NotificationFacadeSpy()
    notification_port = NotificationPortSpy()
    service = SystemRuntimeAlertsService(startup_facade, notification_port, settings)

    monkeypatch.setattr(settings, "runtime_alerts_enabled", False)
    monkeypatch.setattr(settings, "runtime_alerts_chat_id", None)

    await service.notify_startup()
    await service.notify_shutdown()

    assert startup_facade.calls == []
    assert notification_port.message_calls == []


@pytest.mark.asyncio
async def test_runtime_alerts_service_dispatches_startup_via_notification_facade(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    startup_facade = NotificationFacadeSpy()
    notification_port = NotificationPortSpy()
    service = SystemRuntimeAlertsService(startup_facade, notification_port, settings)

    monkeypatch.setattr(settings, "runtime_alerts_enabled", True)
    monkeypatch.setattr(settings, "runtime_alerts_chat_id", 123456789)
    monkeypatch.setattr(settings, "bot_mode", "prod")
    monkeypatch.setattr(settings, "health_api_enabled", True)

    await service.notify_startup()

    assert len(startup_facade.calls) == 1
    notify_dto = startup_facade.calls[0]
    assert notify_dto.recipient_id == 123456789
    assert notify_dto.kind is TaskScheduleKind.IMMEDIATE
    assert "bot startup" in notify_dto.message
    assert "Mode: prod" in notify_dto.message
    assert "Health API: enabled" in notify_dto.message
    assert notification_port.message_calls == []


@pytest.mark.asyncio
async def test_runtime_alerts_service_sends_shutdown_directly_via_notification_port(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    startup_facade = NotificationFacadeSpy()
    notification_port = NotificationPortSpy()
    service = SystemRuntimeAlertsService(startup_facade, notification_port, settings)

    monkeypatch.setattr(settings, "runtime_alerts_enabled", True)
    monkeypatch.setattr(settings, "runtime_alerts_chat_id", 987654321)
    monkeypatch.setattr(settings, "bot_mode", "test")

    await service.notify_shutdown()

    assert startup_facade.calls == []
    assert len(notification_port.message_calls) == 1
    notify_dto = notification_port.message_calls[0]
    assert notify_dto.recipient_id == 987654321
    assert "bot shutdown" in notify_dto.message
    assert "Mode: test" in notify_dto.message
