from types import SimpleNamespace

import pytest
from dishka import make_async_container

from pybot.di import containers as di_containers
from pybot.infrastructure.ports import LoggingNotificationService, TelegramNotificationService
from pybot.services.ports import NotificationPort


def _configure_fake_bot(monkeypatch: pytest.MonkeyPatch, mocker) -> None:
    class FakeBot:
        def __init__(self, token: str) -> None:
            self.token = token
            self.session = SimpleNamespace(close=mocker.AsyncMock())

    monkeypatch.setattr(di_containers, "Bot", FakeBot)
    monkeypatch.setattr(di_containers.settings, "bot_mode", "test")
    monkeypatch.setattr(di_containers.settings, "bot_token_test", "123456:NOTIF_TEST_TOKEN")


@pytest.mark.asyncio
async def test_ports_provider_resolves_logging_backend(
    monkeypatch: pytest.MonkeyPatch,
    mocker,
) -> None:
    _configure_fake_bot(monkeypatch, mocker)
    monkeypatch.setattr(di_containers.settings, "notification_backend", "logging")

    container = make_async_container(
        di_containers.BotProvider(),
        di_containers.PortsProvider(),
    )
    try:
        notification_port = await container.get(NotificationPort)
        assert isinstance(notification_port, LoggingNotificationService)
    finally:
        await container.close()


@pytest.mark.asyncio
async def test_ports_provider_resolves_telegram_backend(
    monkeypatch: pytest.MonkeyPatch,
    mocker,
) -> None:
    _configure_fake_bot(monkeypatch, mocker)
    monkeypatch.setattr(di_containers.settings, "notification_backend", "telegram")

    container = make_async_container(
        di_containers.BotProvider(),
        di_containers.PortsProvider(),
    )
    try:
        notification_port = await container.get(NotificationPort)
        assert isinstance(notification_port, TelegramNotificationService)
    finally:
        await container.close()


@pytest.mark.asyncio
async def test_ports_provider_raises_on_invalid_backend(
    monkeypatch: pytest.MonkeyPatch,
    mocker,
) -> None:
    _configure_fake_bot(monkeypatch, mocker)
    monkeypatch.setattr(di_containers.settings, "notification_backend", "invalid")

    container = make_async_container(
        di_containers.BotProvider(),
        di_containers.PortsProvider(),
    )
    try:
        with pytest.raises(ValueError, match="NOTIFICATION_BACKEND"):
            await container.get(NotificationPort)
    finally:
        await container.close()
