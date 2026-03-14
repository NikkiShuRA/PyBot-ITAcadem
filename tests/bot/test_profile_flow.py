from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, date, datetime
from unittest.mock import AsyncMock

import pytest
from aiogram.types import Chat, Message, User
from aiogram_dialog.api.entities.modes import StartMode

from pybot.bot.dialogs.user_reg.states import CreateProfileSG
from pybot.bot.dialogs.user_reg.windows import prompt_contact_request
from pybot.bot.handlers.common.start import cmd_start_private
from pybot.bot.handlers.profile.user_profile import cmd_profile_private
from pybot.bot.keyboards.auth import request_contact_kb
from pybot.core.constants import LevelTypeEnum
from pybot.dto import UserReadDTO
from pybot.dto.value_objects import Points
from pybot.services import UserProfileService
from pybot.services.users import UserService


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
        academic_points=Points(value=50, point_type=LevelTypeEnum.ACADEMIC),
        reputation_points=Points(value=10, point_type=LevelTypeEnum.REPUTATION),
        join_date=date(2025, 1, 10),
    )


@dataclass(slots=True)
class StubDialogManager:
    start: AsyncMock = field(default_factory=AsyncMock)


@dataclass(slots=True)
class StubRegistrationDialogManager:
    event: Message


class StubUserService(UserService):
    def __init__(self, *, found_user: UserReadDTO | None) -> None:
        self.found_user = found_user
        self.telegram_queries: list[int] = []

    async def find_user_by_telegram_id(self, tg_id: int) -> UserReadDTO | None:
        self.telegram_queries.append(tg_id)
        return self.found_user


class StubUserProfileService(UserProfileService):
    def __init__(self) -> None:
        self.manage_profile_mock = AsyncMock()

    async def manage_profile(self, user_read: UserReadDTO) -> None:
        await self.manage_profile_mock(user_read)


@pytest.mark.asyncio
async def test_cmd_start_private_shows_profile_when_user_exists(monkeypatch: pytest.MonkeyPatch) -> None:
    # Arrange
    message = _build_message()
    dialog_manager = StubDialogManager()
    user = _build_user_read_dto()
    user_service = StubUserService(found_user=user)
    user_profile_service = StubUserProfileService()
    answer_mock = AsyncMock()
    monkeypatch.setattr(Message, "answer", answer_mock)

    # Act
    await cmd_start_private(
        message=message,
        dialog_manager=dialog_manager,
        user_service=user_service,
        user_profile_service=user_profile_service,
    )

    # Assert
    assert user_service.telegram_queries == [700_001]
    user_profile_service.manage_profile_mock.assert_awaited_once_with(user)
    answer_mock.assert_not_awaited()
    dialog_manager.start.assert_not_awaited()


@pytest.mark.asyncio
async def test_cmd_start_private_requests_contact_when_user_is_not_registered(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    # Arrange
    message = _build_message()
    dialog_manager = StubDialogManager()
    user_service = StubUserService(found_user=None)
    user_profile_service = StubUserProfileService()
    answer_mock = AsyncMock()
    monkeypatch.setattr(Message, "answer", answer_mock)

    # Act
    await cmd_start_private(
        message=message,
        dialog_manager=dialog_manager,
        user_service=user_service,
        user_profile_service=user_profile_service,
    )

    # Assert
    assert user_service.telegram_queries == [700_001]
    user_profile_service.manage_profile_mock.assert_not_awaited()
    answer_mock.assert_not_awaited()
    dialog_manager.start.assert_awaited_once_with(CreateProfileSG.contact, mode=StartMode.RESET_STACK)


@pytest.mark.asyncio
async def test_cmd_profile_private_shows_profile_when_user_exists(monkeypatch: pytest.MonkeyPatch) -> None:
    # Arrange
    message = _build_message()
    dialog_manager = StubDialogManager()
    user = _build_user_read_dto()
    user_service = StubUserService(found_user=user)
    user_profile_service = StubUserProfileService()
    answer_mock = AsyncMock()
    monkeypatch.setattr(Message, "answer", answer_mock)

    # Act
    await cmd_profile_private(
        message=message,
        dialog_manager=dialog_manager,
        user_service=user_service,
        user_profile_service=user_profile_service,
    )

    # Assert
    assert user_service.telegram_queries == [700_001]
    user_profile_service.manage_profile_mock.assert_awaited_once_with(user)
    answer_mock.assert_not_awaited()
    dialog_manager.start.assert_not_awaited()


@pytest.mark.asyncio
async def test_cmd_profile_private_requests_contact_when_user_is_not_registered(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    # Arrange
    message = _build_message()
    dialog_manager = StubDialogManager()
    user_service = StubUserService(found_user=None)
    user_profile_service = StubUserProfileService()
    answer_mock = AsyncMock()
    monkeypatch.setattr(Message, "answer", answer_mock)

    # Act
    await cmd_profile_private(
        message=message,
        dialog_manager=dialog_manager,
        user_service=user_service,
        user_profile_service=user_profile_service,
    )

    # Assert
    assert user_service.telegram_queries == [700_001]
    user_profile_service.manage_profile_mock.assert_not_awaited()
    answer_mock.assert_not_awaited()
    dialog_manager.start.assert_awaited_once_with(CreateProfileSG.contact, mode=StartMode.RESET_STACK)


@pytest.mark.asyncio
async def test_cmd_profile_private_requests_contact_when_message_sender_is_missing(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    # Arrange
    message = _build_message(from_user_id=None)
    dialog_manager = StubDialogManager()
    user_service = StubUserService(found_user=None)
    user_profile_service = StubUserProfileService()
    answer_mock = AsyncMock()
    monkeypatch.setattr(Message, "answer", answer_mock)

    # Act
    await cmd_profile_private(
        message=message,
        dialog_manager=dialog_manager,
        user_service=user_service,
        user_profile_service=user_profile_service,
    )

    # Assert
    assert user_service.telegram_queries == []
    user_profile_service.manage_profile_mock.assert_not_awaited()
    answer_mock.assert_not_awaited()
    dialog_manager.start.assert_awaited_once_with(CreateProfileSG.contact, mode=StartMode.RESET_STACK)


@pytest.mark.asyncio
async def test_prompt_contact_request_sends_contact_keyboard(monkeypatch: pytest.MonkeyPatch) -> None:
    message = _build_message()
    manager = StubRegistrationDialogManager(event=message)
    answer_mock = AsyncMock()
    monkeypatch.setattr(Message, "answer", answer_mock)

    await prompt_contact_request(None, manager)  # type: ignore[arg-type]

    answer_mock.assert_awaited_once_with(
        "Пожалуйста, отправьте свой контакт, используя кнопку ниже.",
        reply_markup=request_contact_kb,
    )
