import pytest

from pybot.infrastructure.ports import logging_notification_service as logging_module
from pybot.infrastructure.ports.logging_notification_service import LoggingNotificationService


@pytest.mark.asyncio
async def test_send_role_request_to_admin_logs_and_buffers_event(
    monkeypatch: pytest.MonkeyPatch,
    mocker,
) -> None:
    service = LoggingNotificationService()
    info_mock = mocker.patch.object(logging_module.logger, "info")

    monkeypatch.setattr(logging_module.settings, "role_request_admin_tg_id", 999123)

    await service.send_role_request_to_admin(
        request_id=42,
        requester_user_id=555666,
        role_name="Admin",
    )

    info_mock.assert_called_once()
    assert len(service.events) == 1
    event = service.events[0]
    assert event.event_type == "role_request_to_admin"
    assert event.recipient_user_id == 999123
    assert event.request_id == 42
    assert event.requester_user_id == 555666
    assert event.role_name == "Admin"
    assert "tg://user?id=555666" in event.message_text


@pytest.mark.asyncio
async def test_send_role_request_to_admin_raises_on_invalid_admin_id(
    monkeypatch: pytest.MonkeyPatch,
    mocker,
) -> None:
    service = LoggingNotificationService()
    error_mock = mocker.patch.object(logging_module.logger, "error")

    monkeypatch.setattr(logging_module.settings, "role_request_admin_tg_id", 0)

    with pytest.raises(ValueError, match="ROLE_REQUEST_ADMIN_TG_ID"):
        await service.send_role_request_to_admin(request_id=1, requester_user_id=2, role_name="Mentor")

    error_mock.assert_called_once()
    assert service.events == ()


@pytest.mark.asyncio
async def test_send_message_logs_trimmed_text_and_buffers_event(mocker) -> None:
    service = LoggingNotificationService()
    info_mock = mocker.patch.object(logging_module.logger, "info")

    await service.send_message(user_id=777, message_text="  hello world  ")

    info_mock.assert_called_once()
    assert len(service.events) == 1
    event = service.events[0]
    assert event.event_type == "direct_message"
    assert event.recipient_user_id == 777
    assert event.message_text == "hello world"
    assert event.request_id is None
    assert event.requester_user_id is None
    assert event.role_name is None


@pytest.mark.asyncio
async def test_send_message_raises_on_invalid_user_id() -> None:
    service = LoggingNotificationService()

    with pytest.raises(ValueError, match="user_id"):
        await service.send_message(user_id=0, message_text="test")

    assert service.events == ()


@pytest.mark.asyncio
async def test_send_message_raises_on_blank_text() -> None:
    service = LoggingNotificationService()

    with pytest.raises(ValueError, match="message_text"):
        await service.send_message(user_id=111, message_text="   ")

    assert service.events == ()


@pytest.mark.asyncio
async def test_ring_buffer_keeps_last_1000_events() -> None:
    service = LoggingNotificationService()

    for idx in range(1005):
        await service.send_message(user_id=idx + 1, message_text=f"msg-{idx}")

    assert len(service.events) == 1000
    assert service.events[0].message_text == "msg-5"
    assert service.events[-1].message_text == "msg-1004"
