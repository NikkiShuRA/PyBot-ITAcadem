from types import SimpleNamespace

import pytest
from dishka import make_async_container

from pybot.core.config import BotSettings
from pybot.di import containers as di_containers
from pybot.infrastructure.ports import LoggingNotificationService, TelegramNotificationService
from pybot.services.ports import NotificationPort


def _configure_fake_bot(
    monkeypatch: pytest.MonkeyPatch,
    mocker,
    settings_obj: BotSettings,
) -> None:
    class FakeBot:
        def __init__(self, token: str, session=None, **_: object) -> None:
            self.token = token
            self.session = session or SimpleNamespace(close=mocker.AsyncMock())

    monkeypatch.setattr(di_containers, "Bot", FakeBot)
    settings_obj.bot_mode = "test"
    settings_obj.bot_token_test = "123456:NOTIF_TEST_TOKEN"
    settings_obj.telegram_proxy_url = None


@pytest.mark.asyncio
async def test_ports_provider_resolves_logging_backend(
    monkeypatch: pytest.MonkeyPatch,
    mocker,
    settings_obj: BotSettings,
) -> None:
    _configure_fake_bot(monkeypatch, mocker, settings_obj)
    settings_obj.notification_backend = "logging"

    container = make_async_container(
        di_containers.ConfigProvider(),
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
    settings_obj: BotSettings,
) -> None:
    _configure_fake_bot(monkeypatch, mocker, settings_obj)
    settings_obj.notification_backend = "telegram"

    container = make_async_container(
        di_containers.ConfigProvider(),
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
    settings_obj: BotSettings,
) -> None:
    _configure_fake_bot(monkeypatch, mocker, settings_obj)
    setattr(settings_obj, "notification_backend", "invalid")

    container = make_async_container(
        di_containers.ConfigProvider(),
        di_containers.BotProvider(),
        di_containers.PortsProvider(),
    )
    try:
        with pytest.raises(ValueError, match="NOTIFICATION_BACKEND"):
            await container.get(NotificationPort)
    finally:
        await container.close()
