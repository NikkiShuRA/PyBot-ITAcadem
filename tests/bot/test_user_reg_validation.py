from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime
from unittest.mock import AsyncMock

import pytest
from aiogram.types import Chat, Message, User
from aiogram_dialog import DialogManager
from aiogram_dialog.widgets.input import MessageInput
from pytest_mock import MockerFixture

from pybot.bot.dialogs.user_reg.handlers import (
    _on_patronymic_input_impl,
    on_first_name_input,
    on_last_name_input,
)
from pybot.services.users import UserService


def _build_message(text: str, user_id: int = 100_001) -> Message:
    sender = User(id=user_id, is_bot=False, first_name="Student")
    return Message(
        message_id=1,
        date=datetime.now(UTC),
        chat=Chat(id=user_id, type="private"),
        from_user=sender,
        text=text,
    )


async def _noop_input_handler(message: Message, widget: MessageInput, manager: DialogManager) -> None:
    return None


def _build_widget() -> MessageInput:
    return MessageInput(_noop_input_handler)


@dataclass(slots=True)
class ManagerTestState:
    manager: DialogManager
    next_mock: AsyncMock
    done_mock: AsyncMock


@dataclass(slots=True)
class UserServiceTestState:
    service: UserService
    register_student_mock: AsyncMock


def _build_manager(mocker: MockerFixture) -> ManagerTestState:
    manager = mocker.create_autospec(DialogManager, instance=True, spec_set=True)
    next_mock = mocker.AsyncMock()
    done_mock = mocker.AsyncMock()

    manager.dialog_data = {}
    manager.next = next_mock
    manager.done = done_mock
    return ManagerTestState(manager=manager, next_mock=next_mock, done_mock=done_mock)


def _build_user_service(mocker: MockerFixture) -> UserServiceTestState:
    service = mocker.create_autospec(UserService, instance=True, spec_set=True)
    register_student_mock = mocker.AsyncMock()
    service.register_student = register_student_mock
    return UserServiceTestState(service=service, register_student_mock=register_student_mock)


@pytest.mark.asyncio
async def test_first_name_with_invalid_symbols_returns_error_and_keeps_state(mocker: MockerFixture) -> None:
    message = _build_message("Ivan123")
    widget = _build_widget()
    manager_state = _build_manager(mocker)
    answer_mock = mocker.patch.object(Message, "answer", new=mocker.AsyncMock())

    await on_first_name_input(message=message, widget=widget, manager=manager_state.manager)

    answer_mock.assert_awaited_once()
    manager_state.next_mock.assert_not_awaited()
    assert "first_name" not in manager_state.manager.dialog_data


@pytest.mark.asyncio
async def test_first_name_valid_moves_to_next_state(mocker: MockerFixture) -> None:
    message = _build_message("Иван")
    widget = _build_widget()
    manager_state = _build_manager(mocker)
    answer_mock = mocker.patch.object(Message, "answer", new=mocker.AsyncMock())

    await on_first_name_input(message=message, widget=widget, manager=manager_state.manager)

    answer_mock.assert_not_awaited()
    manager_state.next_mock.assert_awaited_once()
    assert manager_state.manager.dialog_data["first_name"] == "Иван"


@pytest.mark.asyncio
async def test_last_name_with_invalid_symbols_returns_error_and_keeps_state(mocker: MockerFixture) -> None:
    message = _build_message("Петров!")
    widget = _build_widget()
    manager_state = _build_manager(mocker)
    answer_mock = mocker.patch.object(Message, "answer", new=mocker.AsyncMock())

    await on_last_name_input(message=message, widget=widget, manager=manager_state.manager)

    answer_mock.assert_awaited_once()
    manager_state.next_mock.assert_not_awaited()
    assert "last_name" not in manager_state.manager.dialog_data


@pytest.mark.asyncio
async def test_patronymic_with_invalid_symbols_returns_error_and_keeps_state(mocker: MockerFixture) -> None:
    message = _build_message("Иваныч42")
    widget = _build_widget()
    manager_state = _build_manager(mocker)
    user_service_state = _build_user_service(mocker)
    answer_mock = mocker.patch.object(Message, "answer", new=mocker.AsyncMock())

    await _on_patronymic_input_impl(
        message=message,
        widget=widget,
        manager=manager_state.manager,
        user_service=user_service_state.service,
    )

    answer_mock.assert_awaited_once()
    manager_state.done_mock.assert_not_awaited()
    user_service_state.register_student_mock.assert_not_called()
