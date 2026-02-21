from types import SimpleNamespace

import pytest
from aiogram import Bot as AiogramBot
from dishka import make_async_container

from pybot.di import containers as di_containers


@pytest.mark.asyncio
async def test_container_provides_bot_and_closes_session(
    monkeypatch: pytest.MonkeyPatch,
    mocker,
) -> None:
    class FakeBot:
        def __init__(self, token: str) -> None:
            self.token = token
            self.session = SimpleNamespace(close=mocker.AsyncMock())

    monkeypatch.setattr(di_containers, "Bot", FakeBot)
    monkeypatch.setattr(di_containers.settings, "bot_mode", "test")
    monkeypatch.setattr(di_containers.settings, "bot_token_test", "123456:TEST_TOKEN")

    container = make_async_container(di_containers.BotProvider())
    bot = await container.get(AiogramBot)

    assert isinstance(bot, FakeBot)
    assert bot.token == "123456:TEST_TOKEN"

    await container.close()
    bot.session.close.assert_awaited_once()


@pytest.mark.asyncio
async def test_container_uses_prod_token_when_bot_mode_is_prod(
    monkeypatch: pytest.MonkeyPatch,
    mocker,
) -> None:
    class FakeBot:
        def __init__(self, token: str) -> None:
            self.token = token
            self.session = SimpleNamespace(close=mocker.AsyncMock())

    monkeypatch.setattr(di_containers, "Bot", FakeBot)
    monkeypatch.setattr(di_containers.settings, "bot_mode", "prod")
    monkeypatch.setattr(di_containers.settings, "bot_token", "123456:PROD_TOKEN")
    monkeypatch.setattr(di_containers.settings, "bot_token_test", "123456:TEST_TOKEN")

    container = make_async_container(di_containers.BotProvider())
    bot = await container.get(AiogramBot)

    assert isinstance(bot, FakeBot)
    assert bot.token == "123456:PROD_TOKEN"

    await container.close()
    bot.session.close.assert_awaited_once()
