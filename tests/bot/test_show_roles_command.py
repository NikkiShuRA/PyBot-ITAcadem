from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, date, datetime
from unittest.mock import AsyncMock

import pytest
from aiogram.types import Chat, Message, MessageEntity, User

from pybot.bot.handlers.roles.show_roles import handle_show_roles
from pybot.bot.texts import TARGET_NOT_FOUND
from pybot.core.constants import PointsTypeEnum
from pybot.dto import UserReadDTO
from pybot.dto.value_objects import Points


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
    text: str,
    from_user_id: int,
    reply_user_id: int | None = None,
    text_mention_user_id: int | None = None,
    text_mention_label: str = "Target",
) -> Message:
    sender = User(id=from_user_id, is_bot=False, first_name="Sender")
    reply_message: Message | None = None
    entities: list[MessageEntity] | None = None

    if reply_user_id is not None:
        reply_user = User(id=reply_user_id, is_bot=False, first_name="ReplyTarget")
        reply_message = Message(
            message_id=99,
            date=datetime.now(UTC),
            chat=Chat(id=from_user_id, type="private"),
            from_user=reply_user,
            text="target",
        )

    if text_mention_user_id is not None:
        mention_offset = text.index(text_mention_label)
        entities = [
            MessageEntity(
                type="text_mention",
                offset=mention_offset,
                length=len(text_mention_label),
                user=User(id=text_mention_user_id, is_bot=False, first_name=text_mention_label),
            )
        ]

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

    async def find_user_by_telegram_id(self, tg_id: int) -> UserReadDTO | None:
        return self.users_by_tg.get(tg_id)

    async def get_user(self, user_id: int) -> UserReadDTO:
        return self.users_by_id[user_id]


@dataclass(slots=True)
class StubUserRolesService:
    roles_by_user_id: dict[int, list[str]] = field(default_factory=dict)
    show_calls: list[int] = field(default_factory=list)

    async def find_user_roles(self, user_id: int) -> list[str]:
        self.show_calls.append(user_id)
        return self.roles_by_user_id.get(user_id, [])


def _last_reply(reply_mock: AsyncMock) -> tuple[str, dict[str, object]]:
    assert reply_mock.await_args_list
    await_args = reply_mock.await_args_list[-1]
    return str(await_args.args[0]), dict(await_args.kwargs)


@pytest.mark.asyncio
async def test_showroles_without_target_uses_current_user(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    current_user = _build_user_read_dto(db_id=10, telegram_id=100_010, first_name="Admin")
    user_service = StubUserService(users_by_id={current_user.id: current_user})
    user_roles_service = StubUserRolesService(roles_by_user_id={current_user.id: ["Admin", "Mentor"]})
    message = _build_message(text="/showroles", from_user_id=current_user.telegram_id)
    reply_mock = AsyncMock()
    monkeypatch.setattr(Message, "reply", reply_mock)

    await handle_show_roles(
        message=message,
        user_service=user_service,
        user_roles_service=user_roles_service,
        user_id=current_user.id,
    )

    assert user_roles_service.show_calls == [current_user.id]
    reply_text, reply_kwargs = _last_reply(reply_mock)
    assert reply_kwargs == {}
    assert "Роли пользователя Admin" in reply_text
    assert "- Admin" in reply_text
    assert "- Mentor" in reply_text


@pytest.mark.asyncio
async def test_showroles_with_numeric_target_uses_target_user(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    current_user = _build_user_read_dto(db_id=11, telegram_id=100_011, first_name="Admin")
    target_user = _build_user_read_dto(db_id=12, telegram_id=100_012, first_name="Target")
    user_service = StubUserService(
        users_by_tg={target_user.telegram_id: target_user},
        users_by_id={current_user.id: current_user, target_user.id: target_user},
    )
    user_roles_service = StubUserRolesService(roles_by_user_id={target_user.id: ["Student"]})
    message = _build_message(text=f"/showroles {target_user.telegram_id}", from_user_id=current_user.telegram_id)
    reply_mock = AsyncMock()
    monkeypatch.setattr(Message, "reply", reply_mock)

    await handle_show_roles(
        message=message,
        user_service=user_service,
        user_roles_service=user_roles_service,
        user_id=current_user.id,
    )

    assert user_roles_service.show_calls == [target_user.id]
    reply_text, _ = _last_reply(reply_mock)
    assert "Роли пользователя Target" in reply_text
    assert "- Student" in reply_text


@pytest.mark.asyncio
async def test_showroles_with_reply_uses_reply_target(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    current_user = _build_user_read_dto(db_id=13, telegram_id=100_013, first_name="Admin")
    target_user = _build_user_read_dto(db_id=14, telegram_id=100_014, first_name="ReplyTarget")
    user_service = StubUserService(
        users_by_tg={target_user.telegram_id: target_user},
        users_by_id={current_user.id: current_user},
    )
    user_roles_service = StubUserRolesService(roles_by_user_id={target_user.id: ["Mentor"]})
    message = _build_message(
        text="/showroles",
        from_user_id=current_user.telegram_id,
        reply_user_id=target_user.telegram_id,
    )
    reply_mock = AsyncMock()
    monkeypatch.setattr(Message, "reply", reply_mock)

    await handle_show_roles(
        message=message,
        user_service=user_service,
        user_roles_service=user_roles_service,
        user_id=current_user.id,
    )

    assert user_roles_service.show_calls == [target_user.id]
    reply_text, _ = _last_reply(reply_mock)
    assert "Роли пользователя ReplyTarget" in reply_text
    assert "- Mentor" in reply_text


@pytest.mark.asyncio
async def test_showroles_with_text_mention_uses_mentioned_user(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    current_user = _build_user_read_dto(db_id=15, telegram_id=100_015, first_name="Admin")
    target_user = _build_user_read_dto(db_id=16, telegram_id=100_016, first_name="Mentioned")
    user_service = StubUserService(
        users_by_tg={target_user.telegram_id: target_user},
        users_by_id={current_user.id: current_user},
    )
    user_roles_service = StubUserRolesService(roles_by_user_id={target_user.id: ["Student", "Mentor"]})
    message = _build_message(
        text="/showroles Mentioned",
        from_user_id=current_user.telegram_id,
        text_mention_user_id=target_user.telegram_id,
        text_mention_label="Mentioned",
    )
    reply_mock = AsyncMock()
    monkeypatch.setattr(Message, "reply", reply_mock)

    await handle_show_roles(
        message=message,
        user_service=user_service,
        user_roles_service=user_roles_service,
        user_id=current_user.id,
    )

    assert user_roles_service.show_calls == [target_user.id]
    reply_text, _ = _last_reply(reply_mock)
    assert "Роли пользователя Mentioned" in reply_text
    assert "- Student" in reply_text
    assert "- Mentor" in reply_text


@pytest.mark.asyncio
async def test_showroles_returns_target_not_found_for_invalid_explicit_target(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    current_user = _build_user_read_dto(db_id=17, telegram_id=100_017, first_name="Admin")
    user_service = StubUserService(users_by_id={current_user.id: current_user})
    user_roles_service = StubUserRolesService(roles_by_user_id={current_user.id: ["Admin"]})
    message = _build_message(text="/showroles 999999", from_user_id=current_user.telegram_id)
    reply_mock = AsyncMock()
    monkeypatch.setattr(Message, "reply", reply_mock)

    await handle_show_roles(
        message=message,
        user_service=user_service,
        user_roles_service=user_roles_service,
        user_id=current_user.id,
    )

    assert user_roles_service.show_calls == []
    reply_text, reply_kwargs = _last_reply(reply_mock)
    assert reply_kwargs == {}
    assert reply_text == TARGET_NOT_FOUND


@pytest.mark.asyncio
async def test_showroles_returns_empty_state_when_user_has_no_roles(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    current_user = _build_user_read_dto(db_id=18, telegram_id=100_018, first_name="Admin")
    user_service = StubUserService(users_by_id={current_user.id: current_user})
    user_roles_service = StubUserRolesService(roles_by_user_id={current_user.id: []})
    message = _build_message(text="/showroles", from_user_id=current_user.telegram_id)
    reply_mock = AsyncMock()
    monkeypatch.setattr(Message, "reply", reply_mock)

    await handle_show_roles(
        message=message,
        user_service=user_service,
        user_roles_service=user_roles_service,
        user_id=current_user.id,
    )

    assert user_roles_service.show_calls == [current_user.id]
    reply_text, reply_kwargs = _last_reply(reply_mock)
    assert reply_kwargs == {}
    assert reply_text == "У пользователя Admin пока нет ролей."
