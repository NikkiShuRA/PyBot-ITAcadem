from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime
from types import SimpleNamespace
from typing import cast
from unittest.mock import AsyncMock, Mock

import pytest
from aiogram.types import CallbackQuery, Chat, Message, User
from aiogram_dialog import DialogManager
from aiogram_dialog.widgets.input import MessageInput
from aiogram_dialog.widgets.kbd import Button, ManagedMultiselect
from pytest_mock import MockerFixture

from pybot.bot.dialogs.user_reg.handlers import (
    _on_competence_skip_impl,
    _on_competence_submit_impl,
    _on_patronymic_input_impl,
    _on_patronymic_skip_impl,
    on_competence_selection_changed,
    on_first_name_input,
    on_last_name_input,
    request_contact_prompt,
)
from pybot.bot.keyboards.auth import request_contact_kb
from pybot.presentation.texts import (
    REGISTRATION_CONTACT_PROMPT,
    REGISTRATION_INTERNAL_ERROR,
    REGISTRATION_NAME_INVALID_SYMBOLS,
    registration_profile_created,
)
from pybot.dto.competence_dto import CompetenceReadDTO
from pybot.mappers.user_mappers import map_dialog_data_to_user_registration_dto
from pybot.services import CompetenceService, UserRegistrationService
from pybot.services.user_services import UserProfileService


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
    del message, widget, manager


def _build_widget() -> MessageInput:
    return MessageInput(_noop_input_handler)


@dataclass(slots=True)
class ManagerTestState:
    manager: DialogManager
    next_mock: AsyncMock
    done_mock: AsyncMock


@dataclass(slots=True)
class UserRegistrationServiceTestState:
    service: UserRegistrationService
    register_student_mock: AsyncMock


@dataclass(slots=True)
class UserProfileServiceTestState:
    service: UserProfileService
    build_profile_view_mock: AsyncMock


@dataclass(slots=True)
class CompetenceServiceTestState:
    service: CompetenceService
    find_all_competencies_mock: AsyncMock


def _build_manager(mocker: MockerFixture) -> ManagerTestState:
    manager = mocker.create_autospec(DialogManager, instance=True, spec_set=True)
    next_mock = mocker.AsyncMock()
    done_mock = mocker.AsyncMock()
    manager.dialog_data = {}
    manager.next = next_mock
    manager.done = done_mock
    return ManagerTestState(manager=manager, next_mock=next_mock, done_mock=done_mock)


def _build_user_registration_service(mocker: MockerFixture) -> UserRegistrationServiceTestState:
    service = mocker.create_autospec(UserRegistrationService, instance=True, spec_set=True)
    register_student_mock = mocker.AsyncMock()
    service.register_student = register_student_mock
    return UserRegistrationServiceTestState(service=service, register_student_mock=register_student_mock)


def _build_user_profile_service(mocker: MockerFixture) -> UserProfileServiceTestState:
    service = mocker.create_autospec(UserProfileService, instance=True, spec_set=True)
    build_profile_view_mock = mocker.AsyncMock(return_value=SimpleNamespace())
    service.build_profile_view = build_profile_view_mock
    return UserProfileServiceTestState(service=service, build_profile_view_mock=build_profile_view_mock)


def _build_competence_service(mocker: MockerFixture) -> CompetenceServiceTestState:
    service = mocker.create_autospec(CompetenceService, instance=True, spec_set=True)
    find_all_competencies_mock = mocker.AsyncMock()
    service.find_all_competencies = find_all_competencies_mock
    return CompetenceServiceTestState(service=service, find_all_competencies_mock=find_all_competencies_mock)


def _build_competence_read_dto(competence_id: int, name: str) -> CompetenceReadDTO:
    return CompetenceReadDTO(id=competence_id, name=name, description=None)


@pytest.mark.asyncio
async def test_first_name_with_invalid_symbols_returns_error_and_keeps_state(mocker: MockerFixture) -> None:
    message = _build_message("Ivan123")
    widget = _build_widget()
    manager_state = _build_manager(mocker)
    answer_mock = mocker.patch.object(Message, "answer", new=mocker.AsyncMock())

    await on_first_name_input(message=message, widget=widget, manager=manager_state.manager)

    answer_mock.assert_awaited_once_with(REGISTRATION_NAME_INVALID_SYMBOLS)
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

    answer_mock.assert_awaited_once_with(REGISTRATION_NAME_INVALID_SYMBOLS)
    manager_state.next_mock.assert_not_awaited()
    assert "last_name" not in manager_state.manager.dialog_data


@pytest.mark.asyncio
async def test_patronymic_with_invalid_symbols_returns_error_and_keeps_state(mocker: MockerFixture) -> None:
    message = _build_message("Иваныч42")
    widget = _build_widget()
    manager_state = _build_manager(mocker)
    competence_service_state = _build_competence_service(mocker)
    answer_mock = mocker.patch.object(Message, "answer", new=mocker.AsyncMock())

    await _on_patronymic_input_impl(
        message=message,
        widget=widget,
        manager=manager_state.manager,
        competence_service=competence_service_state.service,
    )

    answer_mock.assert_awaited_once_with(REGISTRATION_NAME_INVALID_SYMBOLS)
    manager_state.next_mock.assert_not_awaited()
    competence_service_state.find_all_competencies_mock.assert_not_awaited()


@pytest.mark.asyncio
async def test_request_contact_prompt_moves_to_contact_step(mocker: MockerFixture) -> None:
    message = _build_message("/start")
    callback = SimpleNamespace(message=message, answer=mocker.AsyncMock())
    manager_state = _build_manager(mocker)
    answer_mock = mocker.patch.object(Message, "answer", new=mocker.AsyncMock())

    await request_contact_prompt(
        callback=cast("CallbackQuery", callback),
        button=cast(Button, None),
        manager=manager_state.manager,
    )

    answer_mock.assert_awaited_once_with(
        REGISTRATION_CONTACT_PROMPT,
        reply_markup=request_contact_kb,
    )
    callback.answer.assert_awaited_once()
    manager_state.next_mock.assert_awaited_once()


@pytest.mark.asyncio
async def test_patronymic_input_loads_competencies_and_moves_to_selection_step(mocker: MockerFixture) -> None:
    message = _build_message("Иванович")
    widget = _build_widget()
    manager_state = _build_manager(mocker)
    competence_service_state = _build_competence_service(mocker)
    competence_service_state.find_all_competencies_mock.return_value = [
        _build_competence_read_dto(1, "Python"),
        _build_competence_read_dto(2, "SQL"),
    ]
    answer_mock = mocker.patch.object(Message, "answer", new=mocker.AsyncMock())

    await _on_patronymic_input_impl(
        message=message,
        widget=widget,
        manager=manager_state.manager,
        competence_service=competence_service_state.service,
    )

    assert manager_state.manager.dialog_data["patronymic"] == "Иванович"
    assert manager_state.manager.dialog_data["registration_competencies"] == [(1, "Python"), (2, "SQL")]
    assert manager_state.manager.dialog_data["competence_ids"] == []
    manager_state.next_mock.assert_awaited_once()
    answer_mock.assert_not_awaited()


@pytest.mark.asyncio
async def test_patronymic_skip_loads_competencies_and_moves_to_selection_step(mocker: MockerFixture) -> None:
    callback = SimpleNamespace(answer=mocker.AsyncMock())
    manager_state = _build_manager(mocker)
    competence_service_state = _build_competence_service(mocker)
    competence_service_state.find_all_competencies_mock.return_value = [
        _build_competence_read_dto(3, "Docker"),
    ]

    await _on_patronymic_skip_impl(
        callback=cast("CallbackQuery", callback),
        manager=manager_state.manager,
        competence_service=competence_service_state.service,
    )

    assert manager_state.manager.dialog_data["patronymic"] is None
    assert manager_state.manager.dialog_data["registration_competencies"] == [(3, "Docker")]
    assert manager_state.manager.dialog_data["competence_ids"] == []
    callback.answer.assert_awaited_once()
    manager_state.next_mock.assert_awaited_once()


@pytest.mark.asyncio
async def test_on_competence_selection_changed_stores_checked_ids(mocker: MockerFixture) -> None:
    manager_state = _build_manager(mocker)
    widget = SimpleNamespace(get_checked=lambda: [1, 2])

    await on_competence_selection_changed(
        callback=cast("CallbackQuery", SimpleNamespace()),
        widget=cast(ManagedMultiselect[int], widget),
        manager=manager_state.manager,
        item_id=2,
    )

    assert manager_state.manager.dialog_data["competence_ids"] == [1, 2]


@pytest.mark.asyncio
async def test_competence_submit_registers_user_and_shows_profile_on_success(mocker: MockerFixture) -> None:
    message = _build_message("/start")
    callback = SimpleNamespace(message=message, answer=mocker.AsyncMock())
    manager_state = _build_manager(mocker)
    manager_state.manager.dialog_data.update(
        {
            "phone_number": "+79990001122",
            "tg_id": 100_001,
            "first_name": "Иван",
            "last_name": "Петров",
            "patronymic": "Иванович",
            "competence_ids": [1, 2],
        }
    )
    user_registration_service_state = _build_user_registration_service(mocker)
    user_profile_service_state = _build_user_profile_service(mocker)
    user_dto = SimpleNamespace()
    created_user = SimpleNamespace(first_name="Иван")
    answer_mock = mocker.patch.object(Message, "answer", new=mocker.AsyncMock())
    render_mock = mocker.patch(
        "pybot.bot.dialogs.user_reg.handlers.render_profile_message",
        new=Mock(return_value="profile text"),
    )
    mocker.patch(
        "pybot.bot.dialogs.user_reg.handlers.map_dialog_data_to_user_registration_dto",
        new=mocker.AsyncMock(return_value=user_dto),
    )
    user_registration_service_state.register_student_mock.return_value = created_user

    await _on_competence_submit_impl(
        callback=cast("CallbackQuery", callback),
        manager=manager_state.manager,
        user_reg_service=user_registration_service_state.service,
        user_profile_service=user_profile_service_state.service,
    )

    user_registration_service_state.register_student_mock.assert_awaited_once_with(user_dto)
    user_profile_service_state.build_profile_view_mock.assert_awaited_once_with(created_user)
    render_mock.assert_called_once()
    assert answer_mock.await_count == 2
    answer_mock.assert_any_await(registration_profile_created("Иван"))
    answer_mock.assert_any_await("profile text", parse_mode="HTML")
    callback.answer.assert_awaited_once()
    manager_state.done_mock.assert_awaited_once()


@pytest.mark.asyncio
async def test_competence_skip_clears_selection_and_registers_user(mocker: MockerFixture) -> None:
    message = _build_message("/start")
    callback = SimpleNamespace(message=message, answer=mocker.AsyncMock())
    manager_state = _build_manager(mocker)
    manager_state.manager.dialog_data.update(
        {
            "phone_number": "+79990001122",
            "tg_id": 100_001,
            "first_name": "Иван",
            "last_name": "Петров",
            "competence_ids": [7, 8],
        }
    )
    user_registration_service_state = _build_user_registration_service(mocker)
    user_profile_service_state = _build_user_profile_service(mocker)
    user_dto = SimpleNamespace()
    created_user = SimpleNamespace(first_name="Иван")
    answer_mock = mocker.patch.object(Message, "answer", new=mocker.AsyncMock())
    render_mock = mocker.patch(
        "pybot.bot.dialogs.user_reg.handlers.render_profile_message",
        new=Mock(return_value="profile text"),
    )
    mocker.patch(
        "pybot.bot.dialogs.user_reg.handlers.map_dialog_data_to_user_registration_dto",
        new=mocker.AsyncMock(return_value=user_dto),
    )
    user_registration_service_state.register_student_mock.return_value = created_user

    await _on_competence_skip_impl(
        callback=cast("CallbackQuery", callback),
        manager=manager_state.manager,
        user_reg_service=user_registration_service_state.service,
        user_profile_service=user_profile_service_state.service,
    )

    assert manager_state.manager.dialog_data["competence_ids"] == []
    user_registration_service_state.register_student_mock.assert_awaited_once_with(user_dto)
    user_profile_service_state.build_profile_view_mock.assert_awaited_once_with(created_user)
    render_mock.assert_called_once()
    assert answer_mock.await_count == 2
    answer_mock.assert_any_await(registration_profile_created("Иван"))
    answer_mock.assert_any_await("profile text", parse_mode="HTML")
    callback.answer.assert_awaited_once()
    manager_state.done_mock.assert_awaited_once()


@pytest.mark.asyncio
async def test_competence_submit_reports_internal_error_with_message_and_finishes(mocker: MockerFixture) -> None:
    message = _build_message("/start")
    callback = SimpleNamespace(message=message, answer=mocker.AsyncMock())
    manager_state = _build_manager(mocker)
    user_registration_service_state = _build_user_registration_service(mocker)
    user_profile_service_state = _build_user_profile_service(mocker)
    answer_mock = mocker.patch.object(Message, "answer", new=mocker.AsyncMock())
    mocker.patch(
        "pybot.bot.dialogs.user_reg.handlers.map_dialog_data_to_user_registration_dto",
        new=mocker.AsyncMock(return_value=None),
    )

    await _on_competence_submit_impl(
        callback=cast("CallbackQuery", callback),
        manager=manager_state.manager,
        user_reg_service=user_registration_service_state.service,
        user_profile_service=user_profile_service_state.service,
    )

    user_registration_service_state.register_student_mock.assert_not_awaited()
    user_profile_service_state.build_profile_view_mock.assert_not_awaited()
    answer_mock.assert_awaited_once_with(REGISTRATION_INTERNAL_ERROR)
    callback.answer.assert_awaited_once_with()
    manager_state.done_mock.assert_awaited_once()


@pytest.mark.asyncio
async def test_map_dialog_data_to_user_registration_dto_returns_dto_with_competence_ids(
    mocker: MockerFixture,
) -> None:
    manager_state = _build_manager(mocker)
    manager_state.manager.dialog_data.update(
        {
            "phone_number": "+79990001122",
            "tg_id": 100_001,
            "first_name": "Иван",
            "last_name": "Петров",
            "patronymic": "Иванович",
            "competence_ids": [1, 2, 2],
        }
    )

    result = await map_dialog_data_to_user_registration_dto(manager_state.manager)

    assert result is not None
    assert result.user.first_name == "Иван"
    assert list(result.competence_ids) == [1, 2, 2]
    manager_state.done_mock.assert_not_awaited()


@pytest.mark.asyncio
async def test_map_dialog_data_to_user_registration_dto_uses_empty_competence_ids_by_default(
    mocker: MockerFixture,
) -> None:
    manager_state = _build_manager(mocker)
    manager_state.manager.dialog_data.update(
        {
            "phone_number": "+79990001122",
            "tg_id": 100_001,
            "first_name": "Иван",
            "last_name": "Петров",
        }
    )

    result = await map_dialog_data_to_user_registration_dto(manager_state.manager)

    assert result is not None
    assert tuple(result.competence_ids) == ()
    manager_state.done_mock.assert_not_awaited()
