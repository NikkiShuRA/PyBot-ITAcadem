from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from types import SimpleNamespace
from typing import cast
from unittest.mock import AsyncMock, Mock

import pytest
from aiogram.types import Chat, Message, MessageEntity, User

from pybot.presentation.bot import change_roles_handlers as change_roles
from pybot.presentation.texts import (
    ROLE_COMMAND_INVALID_FORMAT,
    ROLE_REASON_QUOTES_REQUIRED,
    ROLE_UNEXPECTED_ERROR,
    TARGET_NOT_FOUND,
    role_add_success,
    role_not_specified,
    role_remove_success,
    role_target_required,
    role_unknown,
    target_selected_mention,
    target_selected_reply,
)
from pybot.core.constants import RoleEnum
from pybot.domain.exceptions import InvalidRoleChangeError, RoleNotFoundError, UserNotFoundError
from pybot.services.user_services import UserService


def _build_message(
    *,
    text: str | None,
    from_user_id: int = 710_001,
    reply_user_id: int | None = None,
    reply_username: str | None = None,
    entities: list[MessageEntity] | None = None,
) -> Message:
    sender = User(id=from_user_id, is_bot=False, first_name="Admin", username="admin")
    reply_message: Message | None = None

    if reply_user_id is not None:
        target_user = User(
            id=reply_user_id,
            is_bot=False,
            first_name="Target",
            username=reply_username,
        )
        reply_message = Message(
            message_id=99,
            date=datetime.now(UTC),
            chat=Chat(id=from_user_id, type="private"),
            from_user=target_user,
            text="target",
        )

    return Message(
        message_id=1,
        date=datetime.now(UTC),
        chat=Chat(id=from_user_id, type="private"),
        from_user=sender,
        text=text,
        entities=entities,
        reply_to_message=reply_message,
    )


@dataclass(slots=True)
class StubUserService:
    find_user_by_telegram_id: AsyncMock = field(default_factory=AsyncMock)


@dataclass(slots=True)
class StubUserRolesService:
    add_user_role: AsyncMock = field(default_factory=AsyncMock)
    remove_user_role: AsyncMock = field(default_factory=AsyncMock)


def _reply_texts(reply_mock: AsyncMock) -> list[str]:
    return [str(await_call.args[0]) for await_call in reply_mock.await_args_list]


def _last_reply_text(reply_mock: AsyncMock) -> str:
    assert reply_mock.await_args_list
    return _reply_texts(reply_mock)[-1]


@pytest.mark.asyncio
async def test_get_target_user_id_from_reply_with_reply_returns_target_and_confirms_selection(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    message = _build_message(
        text='/addrole Admin "Because"',
        reply_user_id=810_002,
        reply_username="target_user",
    )
    reply_mock = AsyncMock()
    monkeypatch.setattr(Message, "reply", reply_mock)

    target_id = await change_roles._get_target_user_id_from_reply(message)

    assert target_id == 810_002
    reply_mock.assert_awaited_once_with(target_selected_reply("target_user"))


@pytest.mark.asyncio
async def test_get_target_user_id_from_reply_without_reply_returns_none(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    message = _build_message(text='/addrole Admin "Because"')
    reply_mock = AsyncMock()
    monkeypatch.setattr(Message, "reply", reply_mock)

    target_id = await change_roles._get_target_user_id_from_reply(message)

    assert target_id is None
    reply_mock.assert_not_awaited()


@pytest.mark.asyncio
async def test_get_target_user_id_from_mention_without_entities_returns_none(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    message = _build_message(text='/addrole Admin "Because"', entities=None)
    user_service = StubUserService()
    reply_mock = AsyncMock()
    monkeypatch.setattr(Message, "reply", reply_mock)

    target_id = await change_roles._get_target_user_id_from_mention(message, cast(UserService, user_service))

    assert target_id is None
    user_service.find_user_by_telegram_id.assert_not_awaited()
    reply_mock.assert_not_awaited()


@pytest.mark.asyncio
async def test_get_target_user_id_from_mention_when_service_raises_user_not_found_replies_target_not_found(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    mentioned_user = User(id=820_002, is_bot=False, first_name="Mentioned")
    message = _build_message(
        text='/addrole Mentioned Admin "Because"',
        entities=[MessageEntity(type="text_mention", offset=9, length=9, user=mentioned_user)],
    )
    user_service = StubUserService(
        find_user_by_telegram_id=AsyncMock(side_effect=UserNotFoundError(telegram_id=mentioned_user.id))
    )
    reply_mock = AsyncMock()
    monkeypatch.setattr(Message, "reply", reply_mock)

    target_id = await change_roles._get_target_user_id_from_mention(message, cast(UserService, user_service))

    assert target_id is None
    reply_mock.assert_awaited_once_with(TARGET_NOT_FOUND)


@pytest.mark.asyncio
async def test_get_target_user_id_from_mention_when_service_returns_none_replies_target_not_found(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    mentioned_user = User(id=830_002, is_bot=False, first_name="Mentioned")
    message = _build_message(
        text='/addrole Mentioned Admin "Because"',
        entities=[MessageEntity(type="text_mention", offset=9, length=9, user=mentioned_user)],
    )
    user_service = StubUserService(find_user_by_telegram_id=AsyncMock(return_value=None))
    reply_mock = AsyncMock()
    monkeypatch.setattr(Message, "reply", reply_mock)

    target_id = await change_roles._get_target_user_id_from_mention(message, cast(UserService, user_service))

    assert target_id is None
    reply_mock.assert_awaited_once_with(TARGET_NOT_FOUND)


@pytest.mark.asyncio
async def test_get_target_user_id_from_mention_when_user_resolved_returns_telegram_id(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    mentioned_user = User(id=840_002, is_bot=False, first_name="Mentioned")
    resolved_user = SimpleNamespace(first_name="Target", telegram_id=840_555)
    message = _build_message(
        text='/addrole Mentioned Admin "Because"',
        entities=[MessageEntity(type="text_mention", offset=9, length=9, user=mentioned_user)],
    )
    user_service = StubUserService(find_user_by_telegram_id=AsyncMock(return_value=resolved_user))
    reply_mock = AsyncMock()
    monkeypatch.setattr(Message, "reply", reply_mock)

    target_id = await change_roles._get_target_user_id_from_mention(message, cast(UserService, user_service))

    assert target_id == 840_555
    reply_mock.assert_awaited_once_with(target_selected_mention("Target"))


@pytest.mark.asyncio
async def test_extract_role_and_reason_parses_quoted_reason(monkeypatch: pytest.MonkeyPatch) -> None:
    message = _build_message(text='/addrole @mentor Admin "For great mentoring"')
    reply_mock = AsyncMock()
    monkeypatch.setattr(Message, "reply", reply_mock)

    role, reason = await change_roles._extract_role_and_reason(message)

    assert role is RoleEnum.ADMIN
    assert reason == "For great mentoring"
    reply_mock.assert_not_awaited()


@pytest.mark.asyncio
async def test_extract_role_and_reason_accepts_command_without_reason(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    message = _build_message(text="/addrole Admin")
    reply_mock = AsyncMock()
    monkeypatch.setattr(Message, "reply", reply_mock)

    role, reason = await change_roles._extract_role_and_reason(message)

    assert role is RoleEnum.ADMIN
    assert reason is None
    reply_mock.assert_not_awaited()


@pytest.mark.asyncio
async def test_extract_role_and_reason_when_text_is_invalid_replies_invalid_format(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    message = _build_message(text=None)
    reply_mock = AsyncMock()
    monkeypatch.setattr(Message, "reply", reply_mock)

    role, reason = await change_roles._extract_role_and_reason(message)

    assert role is None
    assert reason is None
    reply_mock.assert_awaited_once_with(ROLE_COMMAND_INVALID_FORMAT)


@pytest.mark.asyncio
async def test_extract_role_and_reason_when_role_missing_replies_role_not_specified(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    message = _build_message(text='/addrole @mentor "Because we need help"')
    reply_mock = AsyncMock()
    monkeypatch.setattr(Message, "reply", reply_mock)

    role, reason = await change_roles._extract_role_and_reason(message)

    assert role is None
    assert reason is None
    reply_mock.assert_awaited_once_with(role_not_specified())


@pytest.mark.asyncio
async def test_extract_role_and_reason_when_role_enum_raises_value_error_replies_role_unknown(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    class FakeRoleEnum:
        def __iter__(self) -> object:
            return iter([SimpleNamespace(value="Admin")])

        def __call__(self, value: str) -> RoleEnum:
            raise ValueError(value)

    message = _build_message(text="/addrole Admin")
    reply_mock = AsyncMock()
    monkeypatch.setattr(Message, "reply", reply_mock)
    monkeypatch.setattr(change_roles, "RoleEnum", FakeRoleEnum())

    role, reason = await change_roles._extract_role_and_reason(message)

    assert role is None
    assert reason is None
    reply_mock.assert_awaited_once_with(role_unknown())


@pytest.mark.asyncio
async def test_extract_role_and_reason_rejects_unquoted_reason(monkeypatch: pytest.MonkeyPatch) -> None:
    message = _build_message(text="/addrole Admin because we need help")
    reply_mock = AsyncMock()
    monkeypatch.setattr(Message, "reply", reply_mock)

    role, reason = await change_roles._extract_role_and_reason(message)

    assert role is None
    assert reason is None
    reply_mock.assert_awaited_once_with(ROLE_REASON_QUOTES_REQUIRED)


@pytest.mark.asyncio
async def test_handle_set_role_explains_how_to_select_target_user(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    message = _build_message(text="/addrole Admin")
    user_service = StubUserService()
    user_roles_service = StubUserRolesService()
    reply_mock = AsyncMock()
    monkeypatch.setattr(Message, "reply", reply_mock)

    await change_roles.handle_set_role(
        message=message,
        user_service=user_service,
        user_roles_service=user_roles_service,
        user_id=999_999,
    )

    user_roles_service.add_user_role.assert_not_awaited()
    reply_mock.assert_awaited_once_with(role_target_required("addrole"))


@pytest.mark.asyncio
async def test_handle_set_role_with_reply_target_adds_role_and_replies_success(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    updated_user = SimpleNamespace(first_name="Target")
    message = _build_message(
        text='/addrole Admin "For mentoring"',
        reply_user_id=850_002,
        reply_username="target_user",
    )
    user_service = StubUserService()
    user_roles_service = StubUserRolesService(add_user_role=AsyncMock(return_value=updated_user))
    reply_mock = AsyncMock()
    monkeypatch.setattr(Message, "reply", reply_mock)

    await change_roles.handle_set_role(
        message=message,
        user_service=user_service,
        user_roles_service=user_roles_service,
        user_id=999_999,
    )

    user_roles_service.add_user_role.assert_awaited_once_with(
        telegram_id=850_002,
        new_role=RoleEnum.ADMIN,
    )
    assert _reply_texts(reply_mock) == [
        target_selected_reply("target_user"),
        role_add_success("Target", RoleEnum.ADMIN.value, "For mentoring"),
    ]


@pytest.mark.asyncio
async def test_handle_set_role_when_role_missing_in_service_replies_role_unknown(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    message = _build_message(text='/addrole Admin "For mentoring"', reply_user_id=860_002)
    user_service = StubUserService()
    user_roles_service = StubUserRolesService(
        add_user_role=AsyncMock(side_effect=RoleNotFoundError(RoleEnum.ADMIN.value))
    )
    reply_mock = AsyncMock()
    monkeypatch.setattr(Message, "reply", reply_mock)

    await change_roles.handle_set_role(
        message=message,
        user_service=user_service,
        user_roles_service=user_roles_service,
        user_id=999_999,
    )

    assert _last_reply_text(reply_mock) == role_unknown()


@pytest.mark.asyncio
async def test_handle_set_role_when_role_change_is_invalid_replies_unexpected_error(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    message = _build_message(text='/addrole Admin "For mentoring"', reply_user_id=870_002)
    user_service = StubUserService()
    user_roles_service = StubUserRolesService(
        add_user_role=AsyncMock(side_effect=InvalidRoleChangeError(1, RoleEnum.ADMIN.value, "forbidden"))
    )
    reply_mock = AsyncMock()
    monkeypatch.setattr(Message, "reply", reply_mock)

    await change_roles.handle_set_role(
        message=message,
        user_service=user_service,
        user_roles_service=user_roles_service,
        user_id=999_999,
    )

    assert _last_reply_text(reply_mock) == ROLE_UNEXPECTED_ERROR


@pytest.mark.asyncio
async def test_handle_set_role_when_unexpected_exception_logs_and_replies_unexpected_error(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    message = _build_message(text='/addrole Admin "For mentoring"', reply_user_id=880_002)
    user_service = StubUserService()
    user_roles_service = StubUserRolesService(add_user_role=AsyncMock(side_effect=RuntimeError("boom")))
    reply_mock = AsyncMock()
    logger_exception = Mock()
    monkeypatch.setattr(Message, "reply", reply_mock)
    monkeypatch.setattr(change_roles.logger, "exception", logger_exception)

    await change_roles.handle_set_role(
        message=message,
        user_service=user_service,
        user_roles_service=user_roles_service,
        user_id=999_999,
    )

    logger_exception.assert_called_once_with("Unexpected error in handle_set_role")
    assert _last_reply_text(reply_mock) == ROLE_UNEXPECTED_ERROR


@pytest.mark.asyncio
async def test_handle_remove_role_with_reply_target_removes_role_and_replies_success(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    updated_user = SimpleNamespace(first_name="Target")
    message = _build_message(
        text='/removerole Admin "No longer needed"',
        reply_user_id=890_002,
        reply_username="target_user",
    )
    user_service = StubUserService()
    user_roles_service = StubUserRolesService(remove_user_role=AsyncMock(return_value=updated_user))
    reply_mock = AsyncMock()
    monkeypatch.setattr(Message, "reply", reply_mock)

    await change_roles.handle_remove_role(
        message=message,
        user_service=user_service,
        user_roles_service=user_roles_service,
    )

    user_roles_service.remove_user_role.assert_awaited_once_with(
        tg_id=890_002,
        role_name=RoleEnum.ADMIN.value,
    )
    assert _reply_texts(reply_mock) == [
        target_selected_reply("target_user"),
        role_remove_success("Target", RoleEnum.ADMIN.value, "No longer needed"),
    ]


@pytest.mark.asyncio
async def test_handle_remove_role_when_user_not_found_replies_target_not_found(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    message = _build_message(text='/removerole Admin "No longer needed"', reply_user_id=900_002)
    user_service = StubUserService()
    user_roles_service = StubUserRolesService(
        remove_user_role=AsyncMock(side_effect=UserNotFoundError(telegram_id=900_002))
    )
    reply_mock = AsyncMock()
    monkeypatch.setattr(Message, "reply", reply_mock)

    await change_roles.handle_remove_role(
        message=message,
        user_service=user_service,
        user_roles_service=user_roles_service,
    )

    assert _last_reply_text(reply_mock) == TARGET_NOT_FOUND


@pytest.mark.asyncio
async def test_handle_remove_role_when_role_missing_replies_role_unknown(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    message = _build_message(text='/removerole Admin "No longer needed"', reply_user_id=910_002)
    user_service = StubUserService()
    user_roles_service = StubUserRolesService(
        remove_user_role=AsyncMock(side_effect=RoleNotFoundError(RoleEnum.ADMIN.value))
    )
    reply_mock = AsyncMock()
    monkeypatch.setattr(Message, "reply", reply_mock)

    await change_roles.handle_remove_role(
        message=message,
        user_service=user_service,
        user_roles_service=user_roles_service,
    )

    assert _last_reply_text(reply_mock) == role_unknown()


@pytest.mark.asyncio
async def test_handle_remove_role_when_role_change_is_invalid_replies_unexpected_error(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    message = _build_message(text='/removerole Admin "No longer needed"', reply_user_id=920_002)
    user_service = StubUserService()
    user_roles_service = StubUserRolesService(
        remove_user_role=AsyncMock(side_effect=InvalidRoleChangeError(1, RoleEnum.ADMIN.value, "forbidden"))
    )
    reply_mock = AsyncMock()
    monkeypatch.setattr(Message, "reply", reply_mock)

    await change_roles.handle_remove_role(
        message=message,
        user_service=user_service,
        user_roles_service=user_roles_service,
    )

    assert _last_reply_text(reply_mock) == ROLE_UNEXPECTED_ERROR


@pytest.mark.asyncio
async def test_handle_remove_role_when_unexpected_exception_logs_and_replies_unexpected_error(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    message = _build_message(text='/removerole Admin "No longer needed"', reply_user_id=930_002)
    user_service = StubUserService()
    user_roles_service = StubUserRolesService(remove_user_role=AsyncMock(side_effect=RuntimeError("boom")))
    reply_mock = AsyncMock()
    logger_exception = Mock()
    monkeypatch.setattr(Message, "reply", reply_mock)
    monkeypatch.setattr(change_roles.logger, "exception", logger_exception)

    await change_roles.handle_remove_role(
        message=message,
        user_service=user_service,
        user_roles_service=user_roles_service,
    )

    logger_exception.assert_called_once_with("Unexpected error in handle_remove_role")
    assert _last_reply_text(reply_mock) == ROLE_UNEXPECTED_ERROR
