import asyncio
from types import SimpleNamespace

import pytest

from pybot.bot import tg_bot_run


class DummySpin:
    def __enter__(self) -> "DummySpin":
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        return None

    def ok(self, message: str) -> None:
        return None


@pytest.mark.asyncio
async def test_tg_bot_main_uses_di_bot_and_closes_container(monkeypatch: pytest.MonkeyPatch, mocker) -> None:
    fake_container = SimpleNamespace(close=mocker.AsyncMock())
    fake_bot = SimpleNamespace(
        delete_webhook=mocker.AsyncMock(),
        session=SimpleNamespace(close=mocker.AsyncMock()),
    )
    fake_dp = SimpleNamespace(start_polling=mocker.AsyncMock(side_effect=asyncio.CancelledError()))

    setup_dispatcher_mock = mocker.AsyncMock(return_value=fake_dp)
    setup_di_mock = mocker.AsyncMock(return_value=fake_container)
    setup_bot_mock = mocker.AsyncMock(return_value=fake_bot)
    setup_middlewares_mock = mocker.AsyncMock()
    setup_handlers_mock = mocker.Mock()

    monkeypatch.setattr(tg_bot_run, "setup_dispatcher", setup_dispatcher_mock)
    monkeypatch.setattr(tg_bot_run, "setup_di", setup_di_mock)
    monkeypatch.setattr(tg_bot_run, "setup_bot", setup_bot_mock)
    monkeypatch.setattr(tg_bot_run, "setup_middlewares", setup_middlewares_mock)
    monkeypatch.setattr(tg_bot_run, "setup_handlers", setup_handlers_mock)
    monkeypatch.setattr(tg_bot_run, "yaspin", lambda *args, **kwargs: DummySpin())

    with pytest.raises(asyncio.CancelledError):
        await tg_bot_run.tg_bot_main()

    setup_bot_mock.assert_awaited_once_with(fake_container)
    fake_bot.delete_webhook.assert_awaited_once_with(drop_pending_updates=True)
    fake_dp.start_polling.assert_awaited_once_with(fake_bot)
    fake_container.close.assert_awaited_once()
    fake_bot.session.close.assert_not_awaited()
