import asyncio
from types import SimpleNamespace

import pytest

from pybot.bot import tg_bot_run


@pytest.mark.asyncio
async def test_tg_bot_main_uses_di_bot_and_closes_container(monkeypatch: pytest.MonkeyPatch, mocker) -> None:
    fake_container = SimpleNamespace(close=mocker.AsyncMock())
    fake_bot = SimpleNamespace(
        delete_webhook=mocker.AsyncMock(),
        session=SimpleNamespace(close=mocker.AsyncMock()),
    )
    runtime_alerts_service = SimpleNamespace(
        notify_startup=mocker.AsyncMock(),
        notify_shutdown=mocker.AsyncMock(),
    )
    fake_dp = SimpleNamespace(start_polling=mocker.AsyncMock(side_effect=asyncio.CancelledError()))

    setup_dispatcher_mock = mocker.AsyncMock(return_value=fake_dp)
    setup_di_mock = mocker.AsyncMock(return_value=fake_container)
    setup_bot_mock = mocker.AsyncMock(return_value=fake_bot)
    setup_runtime_alerts_service_mock = mocker.AsyncMock(return_value=runtime_alerts_service)
    setup_middlewares_mock = mocker.AsyncMock()
    setup_handlers_mock = mocker.Mock()

    monkeypatch.setattr(tg_bot_run, "setup_dispatcher", setup_dispatcher_mock)
    monkeypatch.setattr(tg_bot_run, "setup_di", setup_di_mock)
    monkeypatch.setattr(tg_bot_run, "setup_bot", setup_bot_mock)
    monkeypatch.setattr(tg_bot_run, "setup_runtime_alerts_service", setup_runtime_alerts_service_mock)
    monkeypatch.setattr(tg_bot_run, "setup_middlewares", setup_middlewares_mock)
    monkeypatch.setattr(tg_bot_run, "setup_handlers", setup_handlers_mock)

    with pytest.raises(asyncio.CancelledError):
        await tg_bot_run.tg_bot_main()

    setup_bot_mock.assert_awaited_once_with(fake_container)
    setup_runtime_alerts_service_mock.assert_awaited_once_with(fake_container)
    fake_bot.delete_webhook.assert_awaited_once_with(drop_pending_updates=True)
    runtime_alerts_service.notify_startup.assert_awaited_once()
    runtime_alerts_service.notify_shutdown.assert_awaited_once()
    fake_dp.start_polling.assert_awaited_once_with(fake_bot)
    fake_container.close.assert_awaited_once()
    fake_bot.session.close.assert_not_awaited()


@pytest.mark.asyncio
async def test_tg_bot_main_keeps_shutdown_running_when_runtime_alert_delivery_fails(
    monkeypatch: pytest.MonkeyPatch,
    mocker,
) -> None:
    fake_container = SimpleNamespace(close=mocker.AsyncMock())
    fake_bot = SimpleNamespace(
        delete_webhook=mocker.AsyncMock(),
        session=SimpleNamespace(close=mocker.AsyncMock()),
    )
    runtime_alerts_service = SimpleNamespace(
        notify_startup=mocker.AsyncMock(side_effect=RuntimeError("startup alert failed")),
        notify_shutdown=mocker.AsyncMock(side_effect=RuntimeError("shutdown alert failed")),
    )
    fake_dp = SimpleNamespace(start_polling=mocker.AsyncMock(side_effect=asyncio.CancelledError()))

    monkeypatch.setattr(tg_bot_run, "setup_dispatcher", mocker.AsyncMock(return_value=fake_dp))
    monkeypatch.setattr(tg_bot_run, "setup_di", mocker.AsyncMock(return_value=fake_container))
    monkeypatch.setattr(tg_bot_run, "setup_bot", mocker.AsyncMock(return_value=fake_bot))
    monkeypatch.setattr(
        tg_bot_run,
        "setup_runtime_alerts_service",
        mocker.AsyncMock(return_value=runtime_alerts_service),
    )
    monkeypatch.setattr(tg_bot_run, "setup_middlewares", mocker.AsyncMock())
    monkeypatch.setattr(tg_bot_run, "setup_handlers", mocker.Mock())

    with pytest.raises(asyncio.CancelledError):
        await tg_bot_run.tg_bot_main()

    runtime_alerts_service.notify_startup.assert_awaited_once()
    runtime_alerts_service.notify_shutdown.assert_awaited_once()
    fake_container.close.assert_awaited_once()
