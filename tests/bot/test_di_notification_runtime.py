from __future__ import annotations

from types import SimpleNamespace

import pytest
from aiogram import Bot

from pybot.core.config import BotSettings
from pybot.di import containers as di_containers
from pybot.infrastructure.taskiq.taskiq_notification_dispatcher import TaskIQNotificationDispatcher
from pybot.services.notification_facade import NotificationFacade
from pybot.services.ports import NotificationDispatchPort


@pytest.mark.asyncio
async def test_notification_runtime_smoke_resolves_facade_and_dispatcher(
    monkeypatch: pytest.MonkeyPatch,
    mocker,
    settings_obj: BotSettings,
) -> None:
    """Smoke test for the new notification runtime wiring through the public container API."""

    class FakeBot:
        def __init__(self, token: str, session=None, **_: object) -> None:
            self.token = token
            self.session = session or SimpleNamespace(close=mocker.AsyncMock())

    monkeypatch.setattr(di_containers, "Bot", FakeBot)
    settings_obj.bot_token_test = "123456:NOTIFY_TOKEN"
    settings_obj.telegram_proxy_url = None

    container = await di_containers.setup_container()
    try:
        bot = await container.get(Bot)
        dispatch_port = await container.get(NotificationDispatchPort)
        facade = await container.get(NotificationFacade)

        assert isinstance(bot, FakeBot)
        assert isinstance(dispatch_port, TaskIQNotificationDispatcher), (
            "Notification dispatcher wiring drifted. Background notifications would stop using TaskIQ."
        )
        assert isinstance(facade, NotificationFacade), (
            "Notification facade is missing from the app container. Handlers would lose the use-case entrypoint."
        )
        assert facade._dispatch_port is dispatch_port, (
            "Facade and dispatcher are no longer wired together. That usually points to a broken APP-scope setup."
        )
    finally:
        await container.close()
