from types import SimpleNamespace

import pytest
from aiogram import Bot as AiogramBot
from aiogram.client.session.aiohttp import AiohttpSession
from dishka import make_async_container

from pybot.core.config import settings
from pybot.di import containers as di_containers


@pytest.mark.asyncio
async def test_container_provides_bot_and_closes_session(
    monkeypatch: pytest.MonkeyPatch,
    mocker,
) -> None:
    class FakeBot:
        def __init__(self, token: str, session=None, **_: object) -> None:
            self.token = token
            self.session = session or SimpleNamespace(close=mocker.AsyncMock())

    monkeypatch.setattr(di_containers, "Bot", FakeBot)
    monkeypatch.setattr(settings, "bot_mode", "test")
    monkeypatch.setattr(settings, "bot_token_test", "123456:TEST_TOKEN")
    monkeypatch.setattr(settings, "telegram_proxy_url", None)

    container = make_async_container(di_containers.ConfigProvider(), di_containers.BotProvider())
    bot = await container.get(AiogramBot)

    assert isinstance(bot, FakeBot)
    assert bot.token == "123456:TEST_TOKEN"
    assert not isinstance(bot.session, AiohttpSession)

    await container.close()
    bot.session.close.assert_awaited_once()


@pytest.mark.asyncio
async def test_container_uses_prod_token_when_bot_mode_is_prod(
    monkeypatch: pytest.MonkeyPatch,
    mocker,
) -> None:
    class FakeBot:
        def __init__(self, token: str, session=None, **_: object) -> None:
            self.token = token
            self.session = session or SimpleNamespace(close=mocker.AsyncMock())

    monkeypatch.setattr(di_containers, "Bot", FakeBot)
    monkeypatch.setattr(settings, "bot_mode", "prod")
    monkeypatch.setattr(settings, "bot_token", "123456:PROD_TOKEN")
    monkeypatch.setattr(settings, "bot_token_test", "123456:TEST_TOKEN")
    monkeypatch.setattr(settings, "telegram_proxy_url", None)

    container = make_async_container(di_containers.ConfigProvider(), di_containers.BotProvider())
    bot = await container.get(AiogramBot)

    assert isinstance(bot, FakeBot)
    assert bot.token == "123456:PROD_TOKEN"

    await container.close()
    bot.session.close.assert_awaited_once()


@pytest.mark.asyncio
async def test_container_uses_proxy_session_when_proxy_url_is_configured(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    class FakeBot:
        def __init__(self, token: str, session=None, **_: object) -> None:
            self.token = token
            self.session = session

    monkeypatch.setattr(di_containers, "Bot", FakeBot)
    monkeypatch.setattr(settings, "bot_mode", "test")
    monkeypatch.setattr(settings, "bot_token_test", "123456:TEST_TOKEN")
    monkeypatch.setattr(settings, "telegram_proxy_url", "socks5://127.0.0.1:1080")

    container = make_async_container(di_containers.ConfigProvider(), di_containers.BotProvider())
    try:
        bot = await container.get(AiogramBot)

        assert isinstance(bot, FakeBot)
        assert isinstance(bot.session, AiohttpSession)
    finally:
        await container.close()
