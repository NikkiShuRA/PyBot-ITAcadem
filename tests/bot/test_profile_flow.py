from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, date, datetime
from types import SimpleNamespace
from typing import cast
from unittest.mock import AsyncMock, Mock

import pytest
from aiogram.types import CallbackQuery, Chat, Message, User
from aiogram_dialog import DialogManager
from aiogram_dialog.api.entities.modes import StartMode
from aiogram_dialog.widgets.kbd import Button

from pybot.bot.dialogs.user_reg.handlers import request_contact_prompt
from pybot.bot.dialogs.user_reg.states import CreateProfileSG
from pybot.bot.handlers.common.start import cmd_start_private
from pybot.bot.handlers.profile.user_profile import cmd_profile_private
from pybot.bot.keyboards.auth import request_contact_kb
from pybot.bot.texts import REGISTRATION_CONTACT_PROMPT
from pybot.core.constants import PointsTypeEnum
from pybot.dto import UserReadDTO
from pybot.dto.value_objects import Points
from pybot.services.user_services import UserProfileService, UserService


def _build_message(*, from_user_id: int | None = 700_001) -> Message:
    sender = None if from_user_id is None else User(id=from_user_id, is_bot=False, first_name="Tester")
    chat_id = from_user_id if from_user_id is not None else 99_001
    return Message(
        message_id=1,
        date=datetime.now(UTC),
        chat=Chat(id=chat_id, type="private"),
        from_user=sender,
    )


def _build_user_read_dto() -> UserReadDTO:
    return UserReadDTO(
        id=15,
        first_name="Ilya",
        last_name="Tester",
        patronymic=None,
        telegram_id=700_001,
        academic_points=Points(value=50, point_type=PointsTypeEnum.ACADEMIC),
        reputation_points=Points(value=10, point_type=PointsTypeEnum.REPUTATION),
        join_date=date(2025, 1, 10),
    )


@dataclass(slots=True)
class StubDialogManager:
    start: AsyncMock = field(default_factory=AsyncMock)


@dataclass(slots=True)
class StubRegistrationDialogManager:
    next: AsyncMock = field(default_factory=AsyncMock)


class StubUserService(UserService):
    def __init__(self, *, found_user: UserReadDTO | None) -> None:
        self.found_user = found_user
        self.telegram_queries: list[int] = []

    async def find_user_by_telegram_id(self, tg_id: int) -> UserReadDTO | None:
        self.telegram_queries.append(tg_id)
        return self.found_user


class StubUserProfileService:
    def __init__(self) -> None:
        self.profile_view = SimpleNamespace()
        self.build_profile_view_mock = AsyncMock(return_value=self.profile_view)

    async def build_profile_view(self, user_read: UserReadDTO) -> SimpleNamespace:
        return await self.build_profile_view_mock(user_read)


@pytest.mark.asyncio
async def test_cmd_start_private_shows_profile_when_user_exists(monkeypatch: pytest.MonkeyPatch) -> None:
    message = _build_message()
    dialog_manager = StubDialogManager()
    user = _build_user_read_dto()
    user_service = StubUserService(found_user=user)
    user_profile_service = StubUserProfileService()
    answer_mock = AsyncMock()
    render_mock = Mock(return_value="profile text")
    monkeypatch.setattr(Message, "answer", answer_mock)
    monkeypatch.setattr("pybot.bot.handlers.common.start.render_profile_message", render_mock)

    await cmd_start_private(
        message=message,
        dialog_manager=dialog_manager,
        user_service=user_service,
        user_profile_service=cast(UserProfileService, user_profile_service),
    )

    assert user_service.telegram_queries == [700_001]
    user_profile_service.build_profile_view_mock.assert_awaited_once_with(user)
    render_mock.assert_called_once_with(user_profile_service.profile_view)
    answer_mock.assert_awaited_once_with("profile text", parse_mode="HTML")
    dialog_manager.start.assert_not_awaited()


@pytest.mark.asyncio
async def test_cmd_start_private_requests_contact_when_user_is_not_registered(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    message = _build_message()
    dialog_manager = StubDialogManager()
    user_service = StubUserService(found_user=None)
    user_profile_service = StubUserProfileService()
    answer_mock = AsyncMock()
    monkeypatch.setattr(Message, "answer", answer_mock)

    await cmd_start_private(
        message=message,
        dialog_manager=dialog_manager,
        user_service=user_service,
        user_profile_service=cast(UserProfileService, user_profile_service),
    )

    assert user_service.telegram_queries == [700_001]
    user_profile_service.build_profile_view_mock.assert_not_awaited()
    answer_mock.assert_not_awaited()
    dialog_manager.start.assert_awaited_once_with(CreateProfileSG.welcome, mode=StartMode.RESET_STACK)


@pytest.mark.asyncio
async def test_cmd_profile_private_shows_profile_when_user_exists(monkeypatch: pytest.MonkeyPatch) -> None:
    message = _build_message()
    dialog_manager = StubDialogManager()
    user = _build_user_read_dto()
    user_service = StubUserService(found_user=user)
    user_profile_service = StubUserProfileService()
    answer_mock = AsyncMock()
    render_mock = Mock(return_value="profile text")
    monkeypatch.setattr(Message, "answer", answer_mock)
    monkeypatch.setattr("pybot.bot.handlers.profile.user_profile.render_profile_message", render_mock)

    await cmd_profile_private(
        message=message,
        dialog_manager=dialog_manager,
        user_service=user_service,
        user_profile_service=cast(UserProfileService, user_profile_service),
    )

    assert user_service.telegram_queries == [700_001]
    user_profile_service.build_profile_view_mock.assert_awaited_once_with(user)
    render_mock.assert_called_once_with(user_profile_service.profile_view)
    answer_mock.assert_awaited_once_with("profile text", parse_mode="HTML")
    dialog_manager.start.assert_not_awaited()


@pytest.mark.asyncio
async def test_cmd_profile_private_requests_contact_when_user_is_not_registered(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    message = _build_message()
    dialog_manager = StubDialogManager()
    user_service = StubUserService(found_user=None)
    user_profile_service = StubUserProfileService()
    answer_mock = AsyncMock()
    monkeypatch.setattr(Message, "answer", answer_mock)

    await cmd_profile_private(
        message=message,
        dialog_manager=dialog_manager,
        user_service=user_service,
        user_profile_service=cast(UserProfileService, user_profile_service),
    )

    assert user_service.telegram_queries == [700_001]
    user_profile_service.build_profile_view_mock.assert_not_awaited()
    answer_mock.assert_not_awaited()
    dialog_manager.start.assert_awaited_once_with(CreateProfileSG.welcome, mode=StartMode.RESET_STACK)


@pytest.mark.asyncio
async def test_cmd_profile_private_requests_contact_when_message_sender_is_missing(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    message = _build_message(from_user_id=None)
    dialog_manager = StubDialogManager()
    user_service = StubUserService(found_user=None)
    user_profile_service = StubUserProfileService()
    answer_mock = AsyncMock()
    monkeypatch.setattr(Message, "answer", answer_mock)

    await cmd_profile_private(
        message=message,
        dialog_manager=dialog_manager,
        user_service=user_service,
        user_profile_service=cast(UserProfileService, user_profile_service),
    )

    assert user_service.telegram_queries == []
    user_profile_service.build_profile_view_mock.assert_not_awaited()
    answer_mock.assert_not_awaited()
    dialog_manager.start.assert_awaited_once_with(CreateProfileSG.welcome, mode=StartMode.RESET_STACK)


@pytest.mark.asyncio
async def test_request_contact_prompt_sends_contact_keyboard(monkeypatch: pytest.MonkeyPatch) -> None:
    message = _build_message()
    callback = SimpleNamespace(message=message, answer=AsyncMock())
    manager = StubRegistrationDialogManager()
    answer_mock = AsyncMock()
    monkeypatch.setattr(Message, "answer", answer_mock)

    await request_contact_prompt(
        cast("CallbackQuery", callback),
        cast(Button, None),
        cast(DialogManager, manager),
    )

    answer_mock.assert_awaited_once_with(
        REGISTRATION_CONTACT_PROMPT,
        reply_markup=request_contact_kb,
    )
    callback.answer.assert_awaited_once()
    manager.next.assert_awaited_once()
