from __future__ import annotations

import itertools
import time
from datetime import UTC, datetime
from types import SimpleNamespace
from typing import cast
from unittest.mock import AsyncMock

import pytest
from aiogram.types import Chat, Message, User
from dishka import AsyncContainer
from dishka.integrations.aiogram import CONTAINER_NAME
from sqlalchemy.ext.asyncio import AsyncSession

from pybot.core.config import BotSettings
from pybot.presentation.bot import (
    LoggerMiddleware,
    RateLimitMiddleware,
    RoleMiddleware,
    UserActivityMiddleware,
    logger_middleware_module,
)
from tests.factories import UserSpec, attach_user_role, create_role, create_user


def _build_message(*, text: str = "/command", from_user_id: int = 700_001) -> Message:
    sender = User(id=from_user_id, is_bot=False, first_name="Tester")
    return Message(
        message_id=1,
        date=datetime.now(UTC),
        chat=Chat(id=from_user_id, type="private"),
        from_user=sender,
        text=text,
    )


def _build_handler_data(**flags: object) -> dict[str, object]:
    return {"handler": SimpleNamespace(flags=flags)}


@pytest.mark.asyncio
async def test_logger_middleware_reuses_same_event_id_for_start_and_finish_logs(
    monkeypatch: pytest.MonkeyPatch,
    mocker,
    settings_obj: BotSettings,
) -> None:
    settings_obj.enable_logging_middleware = True
    middleware = LoggerMiddleware(settings_obj, enabled=True)
    message = _build_message(text="/start", from_user_id=700_000)
    handler = AsyncMock(return_value="handled")
    data: dict[str, object] = {
        "handler": SimpleNamespace(callback=SimpleNamespace(__name__="cmd_start_private")),
    }

    info_mock = mocker.Mock()
    warning_mock = mocker.Mock()
    debug_mock = mocker.Mock()

    monkeypatch.setattr(logger_middleware_module.logger, "info", info_mock)
    monkeypatch.setattr(logger_middleware_module.logger, "warning", warning_mock)
    monkeypatch.setattr(logger_middleware_module.logger, "debug", debug_mock)

    real_monotonic = time.monotonic
    monotonic_mock = mocker.Mock(side_effect=itertools.chain([10.0, 10.2], itertools.repeat(real_monotonic())))
    monkeypatch.setattr(logger_middleware_module.time, "monotonic", monotonic_mock)

    result = await middleware(handler, message, data)

    assert result == "handled"
    handler.assert_awaited_once_with(message, data)
    warning_mock.assert_not_called()
    assert info_mock.call_count == 2

    first_call = info_mock.call_args_list[0]
    second_call = info_mock.call_args_list[1]
    assert "событие=получен_update" in first_call.args[0]
    assert "событие=обработан_update" in second_call.args[0]
    assert first_call.kwargs["event_id"] == second_call.kwargs["event_id"]
    assert first_call.kwargs["handler_name"] == "cmd_start_private"
    assert second_call.kwargs["handler_name"] == "cmd_start_private"


@pytest.mark.asyncio
async def test_role_middleware_allows_handler_without_role_flag(monkeypatch: pytest.MonkeyPatch) -> None:
    # Given
    middleware = RoleMiddleware()
    message = _build_message()
    handler = AsyncMock(return_value="handled-without-role-check")
    answer_mock = AsyncMock()
    monkeypatch.setattr(Message, "answer", answer_mock)
    data = _build_handler_data()

    # When
    result = await middleware(handler, message, data)

    # Then
    assert result == "handled-without-role-check"
    handler.assert_awaited_once_with(message, data)
    answer_mock.assert_not_awaited()


@pytest.mark.asyncio
async def test_role_middleware_allows_handler_when_event_from_user_is_missing(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    # Given
    middleware = RoleMiddleware()
    message = _build_message()
    handler = AsyncMock(return_value="handled-without-event-user")
    answer_mock = AsyncMock()
    monkeypatch.setattr(Message, "answer", answer_mock)
    data = _build_handler_data(role="Admin")

    # When
    result = await middleware(handler, message, data)

    # Then
    assert result == "handled-without-event-user"
    handler.assert_awaited_once_with(message, data)
    answer_mock.assert_not_awaited()


@pytest.mark.asyncio
async def test_role_middleware_replies_with_auth_error_when_user_id_is_missing(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    # Given
    middleware = RoleMiddleware()
    message = _build_message()
    handler = AsyncMock()
    answer_mock = AsyncMock()
    monkeypatch.setattr(Message, "answer", answer_mock)
    data = _build_handler_data(role="Admin")
    data["event_from_user"] = message.from_user

    # When
    result = await middleware(handler, message, data)

    # Then
    assert result is None
    handler.assert_not_awaited()
    answer_mock.assert_awaited_once()
    await_args = answer_mock.await_args
    assert await_args is not None
    assert "/start" in str(await_args.args[0])


@pytest.mark.asyncio
async def test_role_middleware_allows_user_with_required_role(
    db_session: AsyncSession,
    dishka_test_container: AsyncContainer,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    # Given
    user = await create_user(db_session, spec=UserSpec(telegram_id=700_111))
    admin_role = await create_role(db_session, name="Admin")
    await attach_user_role(db_session, user=user, role=admin_role)
    await db_session.commit()

    middleware = RoleMiddleware()
    message = _build_message(from_user_id=user.telegram_id)
    handler = AsyncMock(return_value="access-granted")
    answer_mock = AsyncMock()
    monkeypatch.setattr(Message, "answer", answer_mock)
    data = _build_handler_data(role="Admin")
    data["event_from_user"] = message.from_user
    data["user_id"] = user.id
    data[CONTAINER_NAME] = dishka_test_container

    # When
    result = await middleware(handler, message, data)

    # Then
    assert result == "access-granted"
    handler.assert_awaited_once_with(message, data)
    answer_mock.assert_not_awaited()


@pytest.mark.asyncio
async def test_role_middleware_blocks_user_without_required_role(
    db_session: AsyncSession,
    dishka_test_container: AsyncContainer,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    # Given
    user = await create_user(db_session, spec=UserSpec(telegram_id=700_222))
    student_role = await create_role(db_session, name="Student")
    await attach_user_role(db_session, user=user, role=student_role)
    await db_session.commit()

    middleware = RoleMiddleware()
    message = _build_message(from_user_id=user.telegram_id)
    handler = AsyncMock()
    answer_mock = AsyncMock()
    monkeypatch.setattr(Message, "answer", answer_mock)
    data = _build_handler_data(role="Admin")
    data["event_from_user"] = message.from_user
    data["user_id"] = user.id
    data[CONTAINER_NAME] = dishka_test_container

    # When
    result = await middleware(handler, message, data)

    # Then
    assert result is None
    handler.assert_not_awaited()
    answer_mock.assert_awaited_once()
    await_args = answer_mock.await_args
    assert await_args is not None
    assert "/start" not in str(await_args.args[0])


@pytest.mark.asyncio
async def test_user_activity_middleware_enriches_data_and_persists_last_activity(
    db_session: AsyncSession,
    dishka_test_container: AsyncContainer,
) -> None:
    # Given
    user = await create_user(db_session, spec=UserSpec(telegram_id=700_333))
    admin_role = await create_role(db_session, name="Admin")
    await attach_user_role(db_session, user=user, role=admin_role)
    await db_session.commit()

    middleware = UserActivityMiddleware()
    message = _build_message(from_user_id=user.telegram_id)
    handler = AsyncMock(return_value="downstream-handler-result")
    data: dict[str, object] = {
        "event_from_user": message.from_user,
        CONTAINER_NAME: dishka_test_container,
    }

    # When
    result = await middleware(handler, message, data)

    # Then
    assert result == "downstream-handler-result"
    handler.assert_awaited_once_with(message, data)
    assert data["user_id"] == user.id
    assert data["user_roles"] == {"Admin"}

    await db_session.refresh(user)
    assert user.last_active_at is not None


@pytest.mark.asyncio
async def test_rate_limit_middleware_skips_limiting_when_flag_is_missing(settings_obj: BotSettings) -> None:
    # Given
    middleware = RateLimitMiddleware(settings_obj)
    message = _build_message(from_user_id=700_444)
    assert message.from_user is not None
    handler = AsyncMock(return_value="handled-without-rate-limit")
    data = _build_handler_data()

    # When
    result = await middleware(handler, message, data)

    # Then
    assert result == "handled-without-rate-limit"
    handler.assert_awaited_once_with(message, data)
    assert await middleware.cache.get(f"{message.from_user.id}:moderate") is None


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ("command_limit", "override_invalid_limit"),
    [
        ("mystery", None),
        ("cheap", (-1, 0)),
    ],
)
async def test_rate_limit_middleware_falls_back_to_moderate_limits(
    command_limit: str,
    override_invalid_limit: tuple[int, int] | None,
    settings_obj: BotSettings,
) -> None:
    # Given
    settings_obj.rate_limit_moderate = 7
    settings_obj.time_limit_moderate = 13
    middleware = RateLimitMiddleware(settings_obj)
    if override_invalid_limit is not None:
        middleware.limits["cheap"] = override_invalid_limit

    message = _build_message(from_user_id=700_555)
    assert message.from_user is not None
    handler = AsyncMock(return_value="handled-with-fallback")
    data = _build_handler_data(rate_limit=command_limit)

    # When
    result = await middleware(handler, message, data)

    # Then
    assert result == "handled-with-fallback"
    handler.assert_awaited_once_with(message, data)
    limiter = await middleware.cache.get(f"{message.from_user.id}:{command_limit}")
    assert limiter is not None
    typed_limiter = cast("object", limiter)
    assert getattr(typed_limiter, "max_rate") == 7
    assert getattr(typed_limiter, "time_period") == 13
