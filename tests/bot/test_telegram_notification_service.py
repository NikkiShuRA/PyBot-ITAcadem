from collections.abc import AsyncGenerator
from dataclasses import dataclass
from math import isclose
from unittest.mock import AsyncMock

import pytest
import pytest_asyncio
from aiogram import Bot
from aiogram.exceptions import TelegramAPIError, TelegramBadRequest, TelegramNetworkError, TelegramRetryAfter
from aiogram.methods import SendMessage
from pytest_mock import MockerFixture

from pybot.bot.keyboards.role_request_keyboard import get_admin_decision_kb
from pybot.core.config import settings
from pybot.infrastructure.ports import telegram_notification_service as notification_module
from pybot.infrastructure.ports.telegram_notification_service import TelegramNotificationService
from pybot.services.ports import NotificationPermanentError, NotificationTemporaryError

ADMIN_TG_ID = 987_654_321
REQUEST_ID = 15
REQUESTER_USER_ID = 111_222_333
RECIPIENT_USER_ID = 321
RETRY_AFTER_SECONDS = 7.0


@dataclass(slots=True)
class BotFixture:
    bot: Bot
    send_message: AsyncMock


def _dummy_method() -> SendMessage:
    return SendMessage(chat_id=1, text="test")


def _expect(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


@pytest_asyncio.fixture
async def fake_bot(mocker: MockerFixture) -> AsyncGenerator[BotFixture, None]:
    bot = Bot(token=settings.bot_token_test)
    send_message_mock: AsyncMock = mocker.AsyncMock()
    mocker.patch.object(bot, "send_message", send_message_mock)
    try:
        yield BotFixture(bot=bot, send_message=send_message_mock)
    finally:
        await bot.session.close()


@pytest.mark.asyncio
async def test_send_role_request_to_admin_sends_message_with_keyboard(
    monkeypatch: pytest.MonkeyPatch,
    fake_bot: BotFixture,
) -> None:
    service = TelegramNotificationService(fake_bot.bot)

    monkeypatch.setattr(notification_module.settings, "role_request_admin_tg_id", ADMIN_TG_ID)

    await service.send_role_request_to_admin(
        request_id=REQUEST_ID,
        requester_user_id=REQUESTER_USER_ID,
        role_name="Admin",
    )

    fake_bot.send_message.assert_awaited_once()
    await_args = fake_bot.send_message.await_args
    _expect(await_args is not None, "send_message has no await args")
    if await_args is None:
        raise AssertionError("send_message has no await args")
    kwargs = await_args.kwargs

    _expect(kwargs.get("chat_id") == ADMIN_TG_ID, "Admin chat id mismatch")
    _expect(kwargs.get("parse_mode") == "HTML", "Parse mode mismatch")
    text = str(kwargs.get("text"))
    _expect(f"Request ID: {REQUEST_ID}" in text, "Request id missing in text")
    _expect(f"tg://user?id={REQUESTER_USER_ID}" in text, "Mention link missing in text")

    expected_markup = get_admin_decision_kb(REQUEST_ID)
    actual_markup = kwargs.get("reply_markup")
    _expect(actual_markup is not None, "Reply markup is missing")
    _expect(
        actual_markup.model_dump() == expected_markup.model_dump(),
        "Reply markup mismatch",
    )


@pytest.mark.asyncio
async def test_send_role_request_to_admin_raises_on_invalid_admin_id(
    monkeypatch: pytest.MonkeyPatch,
    fake_bot: BotFixture,
) -> None:
    service = TelegramNotificationService(fake_bot.bot)

    monkeypatch.setattr(notification_module.settings, "role_request_admin_tg_id", 0)

    with pytest.raises(ValueError, match="ROLE_REQUEST_ADMIN_TG_ID"):
        await service.send_role_request_to_admin(request_id=1, requester_user_id=2, role_name="Admin")

    fake_bot.send_message.assert_not_awaited()


@pytest.mark.asyncio
async def test_send_role_request_to_admin_reraises_bot_error(
    monkeypatch: pytest.MonkeyPatch,
    fake_bot: BotFixture,
) -> None:
    fake_bot.send_message.side_effect = RuntimeError("telegram error")
    service = TelegramNotificationService(fake_bot.bot)

    monkeypatch.setattr(notification_module.settings, "role_request_admin_tg_id", 123_456_789)

    with pytest.raises(RuntimeError, match="telegram error"):
        await service.send_role_request_to_admin(request_id=7, requester_user_id=8, role_name="Mentor")

    fake_bot.send_message.assert_awaited_once()


@pytest.mark.asyncio
async def test_send_message_sends_trimmed_text(fake_bot: BotFixture) -> None:
    service = TelegramNotificationService(fake_bot.bot)

    await service.send_message(user_id=RECIPIENT_USER_ID, message_text="  hello  ")

    fake_bot.send_message.assert_awaited_once_with(chat_id=RECIPIENT_USER_ID, text="hello")


@pytest.mark.asyncio
async def test_send_message_raises_on_blank_text(fake_bot: BotFixture) -> None:
    service = TelegramNotificationService(fake_bot.bot)

    with pytest.raises(ValueError, match="message_text"):
        await service.send_message(user_id=RECIPIENT_USER_ID, message_text="   ")

    fake_bot.send_message.assert_not_awaited()


@pytest.mark.asyncio
async def test_send_message_maps_retry_after_to_temporary_error(fake_bot: BotFixture) -> None:
    fake_bot.send_message.side_effect = TelegramRetryAfter(_dummy_method(), "retry later", int(RETRY_AFTER_SECONDS))
    service = TelegramNotificationService(fake_bot.bot)

    with pytest.raises(NotificationTemporaryError) as exc_info:
        await service.send_message(user_id=RECIPIENT_USER_ID, message_text="hello")

    retry_after = exc_info.value.retry_after_seconds
    _expect(retry_after is not None, "retry_after_seconds must not be None")
    if retry_after is None:
        raise AssertionError("retry_after_seconds must not be None")
    _expect(isclose(retry_after, RETRY_AFTER_SECONDS), "retry_after_seconds mismatch")
    fake_bot.send_message.assert_awaited_once()


@pytest.mark.asyncio
async def test_send_message_maps_network_error_to_temporary_error(fake_bot: BotFixture) -> None:
    fake_bot.send_message.side_effect = TelegramNetworkError(_dummy_method(), "network down")
    service = TelegramNotificationService(fake_bot.bot)

    with pytest.raises(NotificationTemporaryError):
        await service.send_message(user_id=RECIPIENT_USER_ID, message_text="hello")

    fake_bot.send_message.assert_awaited_once()


@pytest.mark.asyncio
async def test_send_message_maps_bad_request_to_permanent_error(fake_bot: BotFixture) -> None:
    fake_bot.send_message.side_effect = TelegramBadRequest(_dummy_method(), "bad request")
    service = TelegramNotificationService(fake_bot.bot)

    with pytest.raises(NotificationPermanentError):
        await service.send_message(user_id=RECIPIENT_USER_ID, message_text="hello")

    fake_bot.send_message.assert_awaited_once()


@pytest.mark.asyncio
async def test_send_message_maps_generic_api_error_to_permanent_error(fake_bot: BotFixture) -> None:
    fake_bot.send_message.side_effect = TelegramAPIError(_dummy_method(), "api failure")
    service = TelegramNotificationService(fake_bot.bot)

    with pytest.raises(NotificationPermanentError):
        await service.send_message(user_id=RECIPIENT_USER_ID, message_text="hello")

    fake_bot.send_message.assert_awaited_once()


@pytest.mark.asyncio
async def test_send_message_maps_unexpected_error_to_permanent_error(fake_bot: BotFixture) -> None:
    fake_bot.send_message.side_effect = RuntimeError("send failed")
    service = TelegramNotificationService(fake_bot.bot)

    with pytest.raises(NotificationPermanentError, match="Unexpected notification delivery failure"):
        await service.send_message(user_id=RECIPIENT_USER_ID, message_text="hello")

    fake_bot.send_message.assert_awaited_once()
