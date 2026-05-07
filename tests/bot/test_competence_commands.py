from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass, field
from datetime import UTC, date, datetime
from typing import cast
from unittest.mock import AsyncMock

import pytest
from aiogram.types import Chat, Message, MessageEntity, User

from pybot.presentation.bot import change_competences_handlers as change_competences
from pybot.presentation.texts import (
    COMPETENCE_UNEXPECTED_ERROR,
    TARGET_NOT_FOUND,
    competence_list_required,
    competence_none,
    competence_validation_error,
)
from pybot.core.constants import PointsTypeEnum
from pybot.domain.exceptions import CommandTargetNotSpecifiedError, CompetenceNotFoundError, UserNotFoundError
from pybot.dto import CompetenceReadDTO, UserReadDTO
from pybot.dto.value_objects import Points
from pybot.services.user_services import UserService


def _build_user_read_dto(db_id: int, telegram_id: int, first_name: str) -> UserReadDTO:
    return UserReadDTO(
        id=db_id,
        first_name=first_name,
        last_name="Test",
        patronymic=None,
        telegram_id=telegram_id,
        academic_points=Points(value=0, point_type=PointsTypeEnum.ACADEMIC),
        reputation_points=Points(value=0, point_type=PointsTypeEnum.REPUTATION),
        join_date=date.today(),
    )


def _build_message(
    *,
    text: str | None,
    from_user_id: int,
    reply_user_id: int | None = None,
    entities: list[MessageEntity] | None = None,
) -> Message:
    sender = User(id=from_user_id, is_bot=False, first_name="Admin")
    reply_message: Message | None = None

    if reply_user_id is not None:
        target_user = User(id=reply_user_id, is_bot=False, first_name="Target")
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
    users_by_tg: dict[int, UserReadDTO] = field(default_factory=dict)
    users_by_id: dict[int, UserReadDTO] = field(default_factory=dict)
    find_error: Exception | None = None
    get_error: Exception | None = None
    telegram_queries: list[int] = field(default_factory=list)
    user_queries: list[int] = field(default_factory=list)

    async def find_user_by_telegram_id(self, tg_id: int) -> UserReadDTO | None:
        self.telegram_queries.append(tg_id)
        if self.find_error is not None:
            raise self.find_error
        return self.users_by_tg.get(tg_id)

    async def get_user(self, user_id: int) -> UserReadDTO | None:
        self.user_queries.append(user_id)
        if self.get_error is not None:
            raise self.get_error
        return self.users_by_id.get(user_id)


@dataclass(slots=True)
class StubUserCompetenceService:
    users_by_id: dict[int, UserReadDTO] = field(default_factory=dict)
    competencies_by_user_id: dict[int, list[CompetenceReadDTO]] = field(default_factory=dict)
    add_calls: list[tuple[int, list[str]]] = field(default_factory=list)
    remove_calls: list[tuple[int, list[str]]] = field(default_factory=list)
    show_calls: list[int] = field(default_factory=list)
    add_exception: Exception | None = None
    remove_exception: Exception | None = None
    show_exception: Exception | None = None

    async def add_user_competencies_by_names(self, user_id: int, competence_names: Sequence[str]) -> UserReadDTO:
        self.add_calls.append((user_id, list(competence_names)))
        if self.add_exception is not None:
            raise self.add_exception
        user = self.users_by_id.get(user_id)
        if user is None:
            raise ValueError("User not found")
        return user

    async def remove_user_competencies_by_names(self, user_id: int, competence_names: Sequence[str]) -> UserReadDTO:
        self.remove_calls.append((user_id, list(competence_names)))
        if self.remove_exception is not None:
            raise self.remove_exception
        user = self.users_by_id.get(user_id)
        if user is None:
            raise ValueError("User not found")
        return user

    async def find_user_competencies(self, user_id: int) -> Sequence[CompetenceReadDTO]:
        self.show_calls.append(user_id)
        if self.show_exception is not None:
            raise self.show_exception
        return self.competencies_by_user_id.get(user_id, [])


@dataclass(slots=True)
class StubCompetenceService:
    competencies: list[CompetenceReadDTO] = field(default_factory=list)
    find_all_exception: Exception | None = None

    async def find_all_competencies(self) -> Sequence[CompetenceReadDTO]:
        if self.find_all_exception is not None:
            raise self.find_all_exception
        return self.competencies


def _last_reply_text(reply_mock: AsyncMock) -> str:
    assert reply_mock.await_args_list
    return str(reply_mock.await_args_list[-1].args[0])


def _reply_texts(reply_mock: AsyncMock) -> list[str]:
    return [str(await_call.args[0]) for await_call in reply_mock.await_args_list]


def test_mask_text_mentions_replaces_text_mention_range_with_spaces() -> None:
    message = _build_message(
        text="/addcompetence @user Python",
        from_user_id=100_000,
        entities=[
            MessageEntity(type="text_mention", offset=15, length=5, user=User(id=1, is_bot=False, first_name="U"))
        ],
    )

    masked = change_competences._mask_text_mentions(message, "/addcompetence @user Python")

    assert masked == "/addcompetence       Python"


def test_mask_text_mentions_clamps_out_of_range_offsets() -> None:
    message = _build_message(
        text="abcde",
        from_user_id=100_001,
        entities=[
            MessageEntity(type="text_mention", offset=-3, length=20, user=User(id=1, is_bot=False, first_name="U"))
        ],
    )

    masked = change_competences._mask_text_mentions(message, "abcde")

    assert masked == "     "


def test_extract_payload_after_command_when_text_invalid_returns_none() -> None:
    message = _build_message(text=None, from_user_id=100_002)

    payload = change_competences._extract_payload_after_command(message)

    assert payload is None


def test_extract_payload_after_command_without_arguments_returns_empty_string() -> None:
    message = _build_message(text="/addcompetence", from_user_id=100_003)

    payload = change_competences._extract_payload_after_command(message)

    assert payload == ""


def test_extract_target_token_from_payload_returns_mention_token() -> None:
    assert change_competences._extract_target_token_from_payload("@mentor Python, SQL") == "@mentor"


def test_extract_target_token_from_payload_returns_numeric_token() -> None:
    assert change_competences._extract_target_token_from_payload("123456 Python, SQL") == "123456"


def test_extract_numeric_target_token_when_payload_starts_with_non_digit_returns_none() -> None:
    message = _build_message(text="/addcompetence @mentor Python", from_user_id=100_004)

    target_id = change_competences._extract_numeric_target_token(message)

    assert target_id is None


def test_has_explicit_target_token_when_payload_has_target_returns_true() -> None:
    message = _build_message(text="/showcompetences 123456", from_user_id=100_005)

    assert change_competences._has_explicit_target_token(message) is True


def test_has_explicit_target_token_when_payload_is_empty_returns_false() -> None:
    message = _build_message(text="/showcompetences", from_user_id=100_006)

    assert change_competences._has_explicit_target_token(message) is False


def test_normalize_competence_names_trims_deduplicates_and_skips_empty_values() -> None:
    normalized = change_competences._normalize_competence_names([" Python ", "sql", "SQL", "", "  "])

    assert normalized == ["Python", "sql"]


def test_extract_competence_names_when_target_source_is_not_reply_strips_target_token() -> None:
    message = _build_message(text="/addcompetence 123456 Python, SQL", from_user_id=100_007)

    names = change_competences._extract_competence_names(message, "text")

    assert names == ["Python", "SQL"]


def test_extract_competence_names_when_target_source_is_reply_keeps_full_payload() -> None:
    message = _build_message(text="/addcompetence Python, SQL", from_user_id=100_008, reply_user_id=200_008)

    names = change_competences._extract_competence_names(message, "reply")

    assert names == ["Python", "SQL"]


@pytest.mark.asyncio
async def test_resolve_target_user_for_command_with_explicit_numeric_target_not_found_raises_telegram_id_error() -> (
    None
):
    user_service = StubUserService()
    message = _build_message(text="/showcompetences 999999", from_user_id=100_009)

    with pytest.raises(UserNotFoundError) as exc_info:
        await change_competences._resolve_target_user_for_command(
            message,
            cast(UserService, user_service),
            command_name="showcompetences",
            required=False,
        )

    assert exc_info.value.details["telegram_id"] == 999999


@pytest.mark.asyncio
async def test_resolve_target_user_for_command_with_explicit_non_numeric_target_raises_generic_user_not_found() -> None:
    user_service = StubUserService()
    message = _build_message(text="/showcompetences @ghost", from_user_id=100_010)

    with pytest.raises(UserNotFoundError) as exc_info:
        await change_competences._resolve_target_user_for_command(
            message,
            cast(UserService, user_service),
            command_name="showcompetences",
            required=False,
        )

    assert exc_info.value.details == {}


@pytest.mark.asyncio
async def test_resolve_target_user_for_command_with_fallback_get_user_returns_current_user() -> None:
    current_user = _build_user_read_dto(db_id=11, telegram_id=200_011, first_name="Admin")
    user_service = StubUserService(users_by_id={current_user.id: current_user})
    message = _build_message(text="/showcompetences", from_user_id=current_user.telegram_id)

    target_user, target_source = await change_competences._resolve_target_user_for_command(
        message,
        cast(UserService, user_service),
        command_name="showcompetences",
        required=False,
        fallback_user_id=current_user.id,
    )

    assert target_user == current_user
    assert target_source is None
    assert user_service.user_queries == [current_user.id]


@pytest.mark.asyncio
async def test_resolve_target_user_for_command_when_fallback_get_user_raises_reraises_with_user_id() -> None:
    user_service = StubUserService(get_error=UserNotFoundError(user_id=77))
    message = _build_message(text="/showcompetences", from_user_id=100_012)

    with pytest.raises(UserNotFoundError) as exc_info:
        await change_competences._resolve_target_user_for_command(
            message,
            cast(UserService, user_service),
            command_name="showcompetences",
            required=False,
            fallback_user_id=77,
        )

    assert exc_info.value.details["user_id"] == 77


@pytest.mark.asyncio
async def test_resolve_target_user_for_command_when_required_and_missing_target_raises_command_target_not_specified() -> (
    None
):
    user_service = StubUserService()
    message = _build_message(text="/addcompetence Python", from_user_id=100_013)

    with pytest.raises(CommandTargetNotSpecifiedError):
        await change_competences._resolve_target_user_for_command(
            message,
            cast(UserService, user_service),
            command_name="addcompetence",
            required=True,
        )


@pytest.mark.asyncio
async def test_addcompetence_by_reply_calls_service_with_csv_names(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    target_user = _build_user_read_dto(db_id=20, telegram_id=200_001, first_name="Target")
    user_service = StubUserService(
        users_by_tg={target_user.telegram_id: target_user},
        users_by_id={target_user.id: target_user},
    )
    user_competence_service = StubUserCompetenceService(users_by_id={target_user.id: target_user})
    message = _build_message(
        text="/addcompetence Python, SQL",
        from_user_id=100_001,
        reply_user_id=target_user.telegram_id,
    )

    reply_mock = AsyncMock()
    monkeypatch.setattr(Message, "reply", reply_mock)

    await change_competences.handle_add_competence(
        message=message,
        user_service=user_service,
        user_competence_service=user_competence_service,
    )

    assert user_competence_service.add_calls == [(target_user.id, ["Python", "SQL"])]
    assert reply_mock.await_count == 1
    reply_text = _last_reply_text(reply_mock)
    assert "Python" in reply_text
    assert "SQL" in reply_text


@pytest.mark.asyncio
async def test_handle_add_competence_when_competence_list_missing_replies_validation_hint(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    target_user = _build_user_read_dto(db_id=21, telegram_id=210_001, first_name="Target")
    user_service = StubUserService(users_by_tg={target_user.telegram_id: target_user})
    user_competence_service = StubUserCompetenceService()
    message = _build_message(
        text="/addcompetence",
        from_user_id=100_101,
        reply_user_id=target_user.telegram_id,
    )
    reply_mock = AsyncMock()
    monkeypatch.setattr(Message, "reply", reply_mock)

    await change_competences.handle_add_competence(
        message=message,
        user_service=user_service,
        user_competence_service=user_competence_service,
    )

    assert _last_reply_text(reply_mock) == competence_list_required("addcompetence")


@pytest.mark.asyncio
async def test_handle_add_competence_when_service_raises_user_not_found_replies_target_not_found(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    target_user = _build_user_read_dto(db_id=22, telegram_id=220_001, first_name="Target")
    user_service = StubUserService(users_by_tg={target_user.telegram_id: target_user})
    user_competence_service = StubUserCompetenceService(add_exception=UserNotFoundError(user_id=target_user.id))
    message = _build_message(
        text="/addcompetence Python",
        from_user_id=100_102,
        reply_user_id=target_user.telegram_id,
    )
    reply_mock = AsyncMock()
    monkeypatch.setattr(Message, "reply", reply_mock)

    await change_competences.handle_add_competence(
        message=message,
        user_service=user_service,
        user_competence_service=user_competence_service,
    )

    assert _last_reply_text(reply_mock) == TARGET_NOT_FOUND


@pytest.mark.asyncio
async def test_handle_add_competence_when_service_raises_value_error_replies_validation_error(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    target_user = _build_user_read_dto(db_id=23, telegram_id=230_001, first_name="Target")
    user_service = StubUserService(users_by_tg={target_user.telegram_id: target_user})
    user_competence_service = StubUserCompetenceService(add_exception=ValueError("bad input"))
    message = _build_message(
        text="/addcompetence Python",
        from_user_id=100_103,
        reply_user_id=target_user.telegram_id,
    )
    reply_mock = AsyncMock()
    monkeypatch.setattr(Message, "reply", reply_mock)

    await change_competences.handle_add_competence(
        message=message,
        user_service=user_service,
        user_competence_service=user_competence_service,
    )

    assert _last_reply_text(reply_mock) == competence_validation_error()


@pytest.mark.asyncio
async def test_handle_add_competence_when_service_raises_unexpected_error_replies_unexpected_error(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    target_user = _build_user_read_dto(db_id=24, telegram_id=240_001, first_name="Target")
    user_service = StubUserService(users_by_tg={target_user.telegram_id: target_user})
    user_competence_service = StubUserCompetenceService(add_exception=RuntimeError("boom"))
    reply_mock = AsyncMock()
    monkeypatch.setattr(Message, "reply", reply_mock)
    message = _build_message(
        text="/addcompetence Python",
        from_user_id=100_104,
        reply_user_id=target_user.telegram_id,
    )

    await change_competences.handle_add_competence(
        message=message,
        user_service=user_service,
        user_competence_service=user_competence_service,
    )

    assert _last_reply_text(reply_mock) == COMPETENCE_UNEXPECTED_ERROR


@pytest.mark.asyncio
async def test_removecompetence_invalid_list_returns_error_message(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    target_user = _build_user_read_dto(db_id=21, telegram_id=200_002, first_name="Target")
    user_service = StubUserService(
        users_by_tg={target_user.telegram_id: target_user},
        users_by_id={target_user.id: target_user},
    )
    user_competence_service = StubUserCompetenceService(
        users_by_id={target_user.id: target_user},
        remove_exception=CompetenceNotFoundError(missing_names=["Unknown"]),
    )
    message = _build_message(text="/removecompetence 200002 Unknown", from_user_id=100_002)

    reply_mock = AsyncMock()
    monkeypatch.setattr(Message, "reply", reply_mock)

    await change_competences.handle_remove_competence(
        message=message,
        user_service=user_service,
        user_competence_service=user_competence_service,
    )

    assert user_competence_service.remove_calls == [(target_user.id, ["Unknown"])]
    reply_text = _last_reply_text(reply_mock)
    assert "Unknown" in reply_text
    assert "Python, SQL" in reply_text


@pytest.mark.asyncio
async def test_handle_remove_competence_when_service_raises_user_not_found_replies_target_not_found(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    target_user = _build_user_read_dto(db_id=25, telegram_id=250_001, first_name="Target")
    user_service = StubUserService(users_by_tg={target_user.telegram_id: target_user})
    user_competence_service = StubUserCompetenceService(remove_exception=UserNotFoundError(user_id=target_user.id))
    message = _build_message(
        text="/removecompetence Python",
        from_user_id=100_105,
        reply_user_id=target_user.telegram_id,
    )
    reply_mock = AsyncMock()
    monkeypatch.setattr(Message, "reply", reply_mock)

    await change_competences.handle_remove_competence(
        message=message,
        user_service=user_service,
        user_competence_service=user_competence_service,
    )

    assert _last_reply_text(reply_mock) == TARGET_NOT_FOUND


@pytest.mark.asyncio
async def test_handle_remove_competence_when_service_raises_value_error_replies_validation_error(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    target_user = _build_user_read_dto(db_id=26, telegram_id=260_001, first_name="Target")
    user_service = StubUserService(users_by_tg={target_user.telegram_id: target_user})
    user_competence_service = StubUserCompetenceService(remove_exception=ValueError("bad input"))
    message = _build_message(
        text="/removecompetence Python",
        from_user_id=100_106,
        reply_user_id=target_user.telegram_id,
    )
    reply_mock = AsyncMock()
    monkeypatch.setattr(Message, "reply", reply_mock)

    await change_competences.handle_remove_competence(
        message=message,
        user_service=user_service,
        user_competence_service=user_competence_service,
    )

    assert _last_reply_text(reply_mock) == competence_validation_error()


@pytest.mark.asyncio
async def test_handle_remove_competence_when_service_raises_unexpected_error_replies_unexpected_error(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    target_user = _build_user_read_dto(db_id=27, telegram_id=270_001, first_name="Target")
    user_service = StubUserService(users_by_tg={target_user.telegram_id: target_user})
    user_competence_service = StubUserCompetenceService(remove_exception=RuntimeError("boom"))
    message = _build_message(
        text="/removecompetence Python",
        from_user_id=100_107,
        reply_user_id=target_user.telegram_id,
    )
    reply_mock = AsyncMock()
    monkeypatch.setattr(Message, "reply", reply_mock)

    await change_competences.handle_remove_competence(
        message=message,
        user_service=user_service,
        user_competence_service=user_competence_service,
    )

    assert _last_reply_text(reply_mock) == COMPETENCE_UNEXPECTED_ERROR


@pytest.mark.asyncio
async def test_showcompetences_without_target_uses_current_user(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    current_user = _build_user_read_dto(db_id=30, telegram_id=300_001, first_name="Admin")
    user_service = StubUserService(
        users_by_id={current_user.id: current_user},
    )
    user_competence_service = StubUserCompetenceService(
        users_by_id={current_user.id: current_user},
        competencies_by_user_id={
            current_user.id: [CompetenceReadDTO(id=1, name="Python", description=None)],
        },
    )
    message = _build_message(text="/showcompetences", from_user_id=current_user.telegram_id)

    reply_mock = AsyncMock()
    monkeypatch.setattr(Message, "reply", reply_mock)

    await change_competences.handle_show_competences(
        message=message,
        user_service=user_service,
        user_competence_service=user_competence_service,
        user_id=current_user.id,
    )

    assert user_competence_service.show_calls == [current_user.id]
    assert "Python" in _last_reply_text(reply_mock)


@pytest.mark.asyncio
async def test_showcompetences_with_target_text_id_uses_target_user(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    target_user = _build_user_read_dto(db_id=40, telegram_id=400_001, first_name="Target")
    admin_user = _build_user_read_dto(db_id=41, telegram_id=400_002, first_name="Admin")
    user_service = StubUserService(
        users_by_tg={target_user.telegram_id: target_user},
        users_by_id={admin_user.id: admin_user, target_user.id: target_user},
    )
    user_competence_service = StubUserCompetenceService(
        users_by_id={target_user.id: target_user},
        competencies_by_user_id={
            target_user.id: [CompetenceReadDTO(id=2, name="SQL", description=None)],
        },
    )
    message = _build_message(text="/showcompetences 400001", from_user_id=admin_user.telegram_id)

    reply_mock = AsyncMock()
    monkeypatch.setattr(Message, "reply", reply_mock)

    await change_competences.handle_show_competences(
        message=message,
        user_service=user_service,
        user_competence_service=user_competence_service,
        user_id=admin_user.id,
    )

    assert user_competence_service.show_calls == [target_user.id]
    reply_text = _last_reply_text(reply_mock)
    assert "Target" in reply_text
    assert "SQL" in reply_text


@pytest.mark.asyncio
async def test_handle_show_competences_when_service_raises_user_not_found_replies_target_not_found(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    current_user = _build_user_read_dto(db_id=31, telegram_id=310_001, first_name="Admin")
    user_service = StubUserService(users_by_id={current_user.id: current_user})
    user_competence_service = StubUserCompetenceService(show_exception=UserNotFoundError(user_id=current_user.id))
    message = _build_message(text="/showcompetences", from_user_id=current_user.telegram_id)
    reply_mock = AsyncMock()
    monkeypatch.setattr(Message, "reply", reply_mock)

    await change_competences.handle_show_competences(
        message=message,
        user_service=user_service,
        user_competence_service=user_competence_service,
        user_id=current_user.id,
    )

    assert _last_reply_text(reply_mock) == TARGET_NOT_FOUND


@pytest.mark.asyncio
async def test_handle_show_competences_when_service_raises_unexpected_error_replies_unexpected_error(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    current_user = _build_user_read_dto(db_id=32, telegram_id=320_001, first_name="Admin")
    user_service = StubUserService(users_by_id={current_user.id: current_user})
    user_competence_service = StubUserCompetenceService(show_exception=RuntimeError("boom"))
    message = _build_message(text="/showcompetences", from_user_id=current_user.telegram_id)
    reply_mock = AsyncMock()
    monkeypatch.setattr(Message, "reply", reply_mock)

    await change_competences.handle_show_competences(
        message=message,
        user_service=user_service,
        user_competence_service=user_competence_service,
        user_id=current_user.id,
    )

    assert _last_reply_text(reply_mock) == COMPETENCE_UNEXPECTED_ERROR


@pytest.mark.asyncio
async def test_handle_show_competences_when_user_has_no_competencies_replies_none_message(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    current_user = _build_user_read_dto(db_id=33, telegram_id=330_001, first_name="Admin")
    user_service = StubUserService(users_by_id={current_user.id: current_user})
    user_competence_service = StubUserCompetenceService()
    message = _build_message(text="/showcompetences", from_user_id=current_user.telegram_id)
    reply_mock = AsyncMock()
    monkeypatch.setattr(Message, "reply", reply_mock)

    await change_competences.handle_show_competences(
        message=message,
        user_service=user_service,
        user_competence_service=user_competence_service,
        user_id=current_user.id,
    )

    assert _last_reply_text(reply_mock) == competence_none(current_user.first_name)


@pytest.mark.asyncio
async def test_addcompetence_unknown_names_returns_validation_error(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    target_user = _build_user_read_dto(db_id=50, telegram_id=500_001, first_name="Target")
    user_service = StubUserService(
        users_by_tg={target_user.telegram_id: target_user},
        users_by_id={target_user.id: target_user},
    )
    user_competence_service = StubUserCompetenceService(
        users_by_id={target_user.id: target_user},
        add_exception=CompetenceNotFoundError(missing_names=["Unknown"]),
    )
    message = _build_message(text="/addcompetence 500001 Unknown", from_user_id=500_002)

    reply_mock = AsyncMock()
    monkeypatch.setattr(Message, "reply", reply_mock)

    await change_competences.handle_add_competence(
        message=message,
        user_service=user_service,
        user_competence_service=user_competence_service,
    )

    assert user_competence_service.add_calls == [(target_user.id, ["Unknown"])]
    reply_text = _last_reply_text(reply_mock)
    assert "Unknown" in reply_text
    assert "Python, SQL" in reply_text


@pytest.mark.asyncio
async def test_addcompetence_distinguishes_missing_target_from_not_found_target(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    user_service = StubUserService(users_by_tg={}, users_by_id={})
    user_competence_service = StubUserCompetenceService()
    missing_target_message = _build_message(text="/addcompetence Python,SQL", from_user_id=600_001)
    not_found_target_message = _build_message(text="/addcompetence 999999 Python,SQL", from_user_id=600_001)
    reply_mock = AsyncMock()
    monkeypatch.setattr(Message, "reply", reply_mock)

    await change_competences.handle_add_competence(
        message=missing_target_message,
        user_service=user_service,
        user_competence_service=user_competence_service,
    )
    first_reply = _reply_texts(reply_mock)[-1]
    assert "/addcompetence" in first_reply

    await change_competences.handle_add_competence(
        message=not_found_target_message,
        user_service=user_service,
        user_competence_service=user_competence_service,
    )
    second_reply = _reply_texts(reply_mock)[-1]
    assert second_reply == TARGET_NOT_FOUND


@pytest.mark.asyncio
async def test_showcompetences_does_not_fallback_on_invalid_explicit_target(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    current_user = _build_user_read_dto(db_id=70, telegram_id=700_701, first_name="Admin")
    user_service = StubUserService(
        users_by_id={current_user.id: current_user},
    )
    user_competence_service = StubUserCompetenceService(
        users_by_id={current_user.id: current_user},
        competencies_by_user_id={
            current_user.id: [CompetenceReadDTO(id=1, name="Python", description=None)],
        },
    )
    message = _build_message(text="/showcompetences 999999", from_user_id=current_user.telegram_id)
    reply_mock = AsyncMock()
    monkeypatch.setattr(Message, "reply", reply_mock)

    await change_competences.handle_show_competences(
        message=message,
        user_service=user_service,
        user_competence_service=user_competence_service,
        user_id=current_user.id,
    )

    assert user_competence_service.show_calls == []
    assert "Python" not in _last_reply_text(reply_mock)


@pytest.mark.asyncio
async def test_competences_command_shows_all_competences_with_html_formatting(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    competence_service = StubCompetenceService(
        competencies=[
            CompetenceReadDTO(id=1, name="Python", description="Язык программирования"),
            CompetenceReadDTO(id=2, name="SQL", description=None),
        ]
    )
    message = _build_message(text="/competences", from_user_id=800_001)
    reply_mock = AsyncMock()
    monkeypatch.setattr(Message, "reply", reply_mock)

    await change_competences.handle_show_all_competences(
        message=message,
        competence_service=competence_service,
    )

    assert reply_mock.await_count == 1
    await_args = reply_mock.await_args
    assert await_args is not None
    assert await_args.kwargs["parse_mode"] == "HTML"
    reply_text = str(await_args.args[0])
    assert "<b>Компетенции:</b>" in reply_text
    assert "<b>Python</b>: Язык программирования." in reply_text
    assert "<b>SQL</b>: Описание не указано." in reply_text


@pytest.mark.asyncio
async def test_handle_show_all_competences_when_service_raises_unexpected_error_replies_unexpected_error(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    competence_service = StubCompetenceService(find_all_exception=RuntimeError("boom"))
    message = _build_message(text="/competences", from_user_id=800_010)
    reply_mock = AsyncMock()
    monkeypatch.setattr(Message, "reply", reply_mock)

    await change_competences.handle_show_all_competences(
        message=message,
        competence_service=competence_service,
    )

    assert _last_reply_text(reply_mock) == COMPETENCE_UNEXPECTED_ERROR


@pytest.mark.asyncio
async def test_competences_command_handles_empty_catalog(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    competence_service = StubCompetenceService(competencies=[])
    message = _build_message(text="/competences", from_user_id=800_002)
    reply_mock = AsyncMock()
    monkeypatch.setattr(Message, "reply", reply_mock)

    await change_competences.handle_show_all_competences(
        message=message,
        competence_service=competence_service,
    )

    assert reply_mock.await_count == 1
    await_args = reply_mock.await_args
    assert await_args is not None
    assert await_args.kwargs["parse_mode"] == "HTML"
    assert "Пока в системе нет доступных компетенций." in str(await_args.args[0])
