from __future__ import annotations

from datetime import UTC, datetime
from unittest.mock import AsyncMock

import pytest
from aiogram.types import CallbackQuery, Chat, Message, User
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from pybot.bot.handlers.roles.role_request_flow import accept_role_request, reject_role_request
from pybot.bot.keyboards.role_request_keyboard import RoleRequestCB
from pybot.core.constants import RequestStatus
from pybot.db.models import RoleRequest
from pybot.services.role_request import RoleRequestService
from tests.factories import RoleRequestSpec, UserSpec, create_role, create_role_request, create_user
from tests.providers import FakeNotificationPort


def _build_callback_query(user_id: int, callback_id: str) -> CallbackQuery:
    from_user = User(id=user_id, is_bot=False, first_name="Admin")
    message = Message(
        message_id=1,
        date=datetime.now(UTC),
        chat=Chat(id=user_id, type="private"),
    )
    return CallbackQuery(
        id=callback_id,
        from_user=from_user,
        chat_instance="role_request_flow",
        data="role_request_action",
        message=message,
    )


def _patch_callback_methods(monkeypatch: pytest.MonkeyPatch) -> tuple[AsyncMock, AsyncMock]:
    answer_mock = AsyncMock()
    edit_reply_markup_mock = AsyncMock()
    monkeypatch.setattr(CallbackQuery, "answer", answer_mock)
    monkeypatch.setattr(Message, "edit_reply_markup", edit_reply_markup_mock)
    return answer_mock, edit_reply_markup_mock


@pytest.mark.asyncio
async def test_accept_role_request_happy_path_updates_status_and_locks_buttons(
    dishka_request_container,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    db = await dishka_request_container.get(AsyncSession)
    role_request_service = await dishka_request_container.get(RoleRequestService)
    notification_service = await dishka_request_container.get(FakeNotificationPort)

    user = await create_user(db, spec=UserSpec(telegram_id=910_001))
    role = await create_role(db, name="Mentor")
    request = await create_role_request(
        db,
        spec=RoleRequestSpec(user=user, role=role, status=RequestStatus.PENDING),
    )
    await db.commit()

    callback_query = _build_callback_query(user_id=920_001, callback_id="approve-happy")
    callback_data = RoleRequestCB(action=RequestStatus.APPROVED, request_id=request.id)

    answer_mock, edit_reply_markup_mock = _patch_callback_methods(monkeypatch)

    await accept_role_request(
        callback_query=callback_query,
        callback_data=callback_data,
        role_request_service=role_request_service,
        notification_service=notification_service,
    )

    updated = (await db.execute(select(RoleRequest).where(RoleRequest.id == request.id))).scalar_one()
    assert updated.status == RequestStatus.APPROVED
    assert await role_request_service.user_repository.has_role(db, user_id=user.id, role_name=role.name) is True

    answer_mock.assert_awaited_once_with("Approved")
    edit_reply_markup_mock.assert_awaited_once_with(reply_markup=None)
    assert any(
        item.user_id == 920_001 and item.message_text == "Role request approved."
        for item in notification_service.direct_messages
    )


@pytest.mark.asyncio
async def test_accept_role_request_already_processed_locks_buttons_and_reports_state(
    dishka_request_container,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    db = await dishka_request_container.get(AsyncSession)
    role_request_service = await dishka_request_container.get(RoleRequestService)
    notification_service = await dishka_request_container.get(FakeNotificationPort)

    user = await create_user(db, spec=UserSpec(telegram_id=910_003))
    role = await create_role(db, name="Mentor")
    request = await create_role_request(
        db,
        spec=RoleRequestSpec(user=user, role=role, status=RequestStatus.APPROVED),
    )
    await db.commit()

    callback_query = _build_callback_query(user_id=920_003, callback_id="approve-already")
    callback_data = RoleRequestCB(action=RequestStatus.APPROVED, request_id=request.id)

    answer_mock, edit_reply_markup_mock = _patch_callback_methods(monkeypatch)

    await accept_role_request(
        callback_query=callback_query,
        callback_data=callback_data,
        role_request_service=role_request_service,
        notification_service=notification_service,
    )

    updated = (await db.execute(select(RoleRequest).where(RoleRequest.id == request.id))).scalar_one()
    assert updated.status == RequestStatus.APPROVED

    answer_mock.assert_awaited_once_with("Already processed")
    edit_reply_markup_mock.assert_awaited_once_with(reply_markup=None)
    assert any(
        item.user_id == 920_003 and item.message_text == "Role request has already been processed."
        for item in notification_service.direct_messages
    )


@pytest.mark.asyncio
async def test_reject_role_request_happy_path_updates_status_and_locks_buttons(
    dishka_request_container,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    db = await dishka_request_container.get(AsyncSession)
    role_request_service = await dishka_request_container.get(RoleRequestService)
    notification_service = await dishka_request_container.get(FakeNotificationPort)

    user = await create_user(db, spec=UserSpec(telegram_id=910_004))
    role = await create_role(db, name="Admin")
    request = await create_role_request(
        db,
        spec=RoleRequestSpec(user=user, role=role, status=RequestStatus.PENDING),
    )
    await db.commit()

    callback_query = _build_callback_query(user_id=920_004, callback_id="reject-happy")
    callback_data = RoleRequestCB(action=RequestStatus.REJECTED, request_id=request.id)

    answer_mock, edit_reply_markup_mock = _patch_callback_methods(monkeypatch)

    await reject_role_request(
        callback_query=callback_query,
        callback_data=callback_data,
        role_request_service=role_request_service,
        notification_service=notification_service,
    )

    updated = (await db.execute(select(RoleRequest).where(RoleRequest.id == request.id))).scalar_one()
    assert updated.status == RequestStatus.REJECTED

    answer_mock.assert_awaited_once_with("Rejected")
    edit_reply_markup_mock.assert_awaited_once_with(reply_markup=None)
    assert any(
        item.user_id == 920_004 and item.message_text == "Role request rejected."
        for item in notification_service.direct_messages
    )


@pytest.mark.asyncio
async def test_reject_role_request_already_processed_locks_buttons_and_reports_state(
    dishka_request_container,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    db = await dishka_request_container.get(AsyncSession)
    role_request_service = await dishka_request_container.get(RoleRequestService)
    notification_service = await dishka_request_container.get(FakeNotificationPort)

    user = await create_user(db, spec=UserSpec(telegram_id=910_002))
    role = await create_role(db, name="Admin")
    request = await create_role_request(
        db,
        spec=RoleRequestSpec(user=user, role=role, status=RequestStatus.APPROVED),
    )
    await db.commit()

    callback_query = _build_callback_query(user_id=920_002, callback_id="reject-already")
    callback_data = RoleRequestCB(action=RequestStatus.REJECTED, request_id=request.id)

    answer_mock, edit_reply_markup_mock = _patch_callback_methods(monkeypatch)

    await reject_role_request(
        callback_query=callback_query,
        callback_data=callback_data,
        role_request_service=role_request_service,
        notification_service=notification_service,
    )

    updated = (await db.execute(select(RoleRequest).where(RoleRequest.id == request.id))).scalar_one()
    assert updated.status == RequestStatus.APPROVED

    answer_mock.assert_awaited_once_with("Already processed")
    edit_reply_markup_mock.assert_awaited_once_with(reply_markup=None)
    assert any(
        item.user_id == 920_002 and item.message_text == "Role request has already been processed."
        for item in notification_service.direct_messages
    )
