from types import SimpleNamespace

import pytest

from pybot.bot.keyboards.role_request_keyboard import get_admin_decision_kb
from pybot.infrastructure.ports import telegram_notification_service as notification_module
from pybot.infrastructure.ports.telegram_notification_service import TelegramNotificationService


@pytest.fixture
def fake_bot(mocker):
    return SimpleNamespace(send_message=mocker.AsyncMock())


@pytest.mark.asyncio
async def test_send_role_request_to_admin_sends_message_with_keyboard(
    monkeypatch: pytest.MonkeyPatch, fake_bot
) -> None:
    service = TelegramNotificationService(fake_bot)

    monkeypatch.setattr(notification_module.settings, "role_request_admin_tg_id", 987654321)

    await service.send_role_request_to_admin(request_id=15, requester_user_id=111222333, role_name="Admin")

    fake_bot.send_message.assert_awaited_once()
    _, kwargs = fake_bot.send_message.await_args

    assert kwargs["chat_id"] == 987654321
    assert kwargs["parse_mode"] == "HTML"
    assert "Новый запрос роли" in kwargs["text"]
    assert "Request ID: 15" in kwargs["text"]
    assert "Роль: Admin" in kwargs["text"]
    assert "tg://user?id=111222333" in kwargs["text"]

    expected_markup = get_admin_decision_kb(15)
    assert kwargs["reply_markup"].model_dump() == expected_markup.model_dump()


@pytest.mark.asyncio
async def test_send_role_request_to_admin_raises_on_invalid_admin_id(monkeypatch: pytest.MonkeyPatch, fake_bot) -> None:
    service = TelegramNotificationService(fake_bot)

    monkeypatch.setattr(notification_module.settings, "role_request_admin_tg_id", 0)

    with pytest.raises(ValueError, match="ROLE_REQUEST_ADMIN_TG_ID"):
        await service.send_role_request_to_admin(request_id=1, requester_user_id=2, role_name="Admin")

    fake_bot.send_message.assert_not_awaited()


@pytest.mark.asyncio
async def test_send_role_request_to_admin_reraises_bot_error(monkeypatch: pytest.MonkeyPatch, fake_bot) -> None:
    fake_bot.send_message.side_effect = RuntimeError("telegram error")
    service = TelegramNotificationService(fake_bot)

    monkeypatch.setattr(notification_module.settings, "role_request_admin_tg_id", 123456789)

    with pytest.raises(RuntimeError, match="telegram error"):
        await service.send_role_request_to_admin(request_id=7, requester_user_id=8, role_name="Mentor")

    fake_bot.send_message.assert_awaited_once()


@pytest.mark.asyncio
async def test_send_message_sends_trimmed_text(fake_bot) -> None:
    service = TelegramNotificationService(fake_bot)

    await service.send_message(user_id=321, message_text="  Привет  ")

    fake_bot.send_message.assert_awaited_once_with(chat_id=321, text="Привет")


@pytest.mark.asyncio
async def test_send_message_raises_on_blank_text(fake_bot) -> None:
    service = TelegramNotificationService(fake_bot)

    with pytest.raises(ValueError, match="message_text"):
        await service.send_message(user_id=321, message_text="   ")

    fake_bot.send_message.assert_not_awaited()


@pytest.mark.asyncio
async def test_send_message_reraises_bot_error(fake_bot) -> None:
    fake_bot.send_message.side_effect = RuntimeError("send failed")
    service = TelegramNotificationService(fake_bot)

    with pytest.raises(RuntimeError, match="send failed"):
        await service.send_message(user_id=321, message_text="Привет")

    fake_bot.send_message.assert_awaited_once()


@pytest.mark.asyncio
async def test_broadcast_is_not_implemented(fake_bot) -> None:
    service = TelegramNotificationService(fake_bot)

    with pytest.raises(NotImplementedError, match="Broadcast is not implemented"):
        await service.broadcast(message_text="Hello", selected_role=None)
