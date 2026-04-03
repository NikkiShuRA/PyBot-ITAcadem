from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from unittest.mock import AsyncMock

import pytest
from aiogram.types import Chat, Message, User

from pybot.bot.handlers.roles.role_catalog import handle_show_all_roles
from pybot.dto import RoleReadDTO


def _build_message(*, text: str = "/roles", from_user_id: int = 900_001) -> Message:
    sender = User(id=from_user_id, is_bot=False, first_name="Tester")
    return Message(
        message_id=1,
        date=datetime.now(UTC),
        chat=Chat(id=from_user_id, type="private"),
        from_user=sender,
        text=text,
    )


@dataclass(slots=True)
class StubUserRolesService:
    roles: list[RoleReadDTO] = field(default_factory=list)
    find_all_roles_mock: AsyncMock = field(init=False)

    def __post_init__(self) -> None:
        self.find_all_roles_mock = AsyncMock(return_value=self.roles)

    async def find_all_roles(self) -> list[RoleReadDTO]:
        return await self.find_all_roles_mock()


@pytest.mark.asyncio
async def test_roles_command_shows_all_roles_with_html_formatting(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    user_roles_service = StubUserRolesService(
        roles=[
            RoleReadDTO(id=1, name="Admin", description="Manages the system"),
            RoleReadDTO(id=2, name="Mentor", description=None),
        ]
    )
    message = _build_message()
    reply_mock = AsyncMock()
    monkeypatch.setattr(Message, "reply", reply_mock)

    await handle_show_all_roles(
        message=message,
        user_roles_service=user_roles_service,
    )

    user_roles_service.find_all_roles_mock.assert_awaited_once_with()
    assert reply_mock.await_count == 1
    await_args = reply_mock.await_args
    assert await_args is not None
    assert await_args.kwargs["parse_mode"] == "HTML"
    reply_text = str(await_args.args[0])
    assert "<b>Роли:</b>" in reply_text
    assert "- <b>Admin</b>: Manages the system" in reply_text
    assert "- <b>Mentor</b>" in reply_text


@pytest.mark.asyncio
async def test_roles_command_handles_empty_catalog(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    user_roles_service = StubUserRolesService(roles=[])
    message = _build_message()
    reply_mock = AsyncMock()
    monkeypatch.setattr(Message, "reply", reply_mock)

    await handle_show_all_roles(
        message=message,
        user_roles_service=user_roles_service,
    )

    user_roles_service.find_all_roles_mock.assert_awaited_once_with()
    assert reply_mock.await_count == 1
    await_args = reply_mock.await_args
    assert await_args is not None
    assert await_args.kwargs["parse_mode"] == "HTML"
    assert "Пока в системе нет доступных ролей." in str(await_args.args[0])
