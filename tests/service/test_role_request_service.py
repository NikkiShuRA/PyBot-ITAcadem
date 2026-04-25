from __future__ import annotations

from datetime import datetime, timedelta

import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from pybot.core.config import BotSettings
from pybot.core.constants import RequestStatus
from pybot.db.models import RoleRequest
from pybot.domain.exceptions import (
    RoleAlreadyAssignedError,
    RoleNotFoundError,
    RoleRequestAlreadyExistsError,
    RoleRequestCooldownError,
    RoleRequestAlreadyProcessedError,
    RoleRequestNotFoundError,
    UserNotFoundError,
)
from pybot.infrastructure.user_repository import UserRepository
from pybot.services.role_request import RoleRequestService
from tests.factories import RoleRequestSpec, UserSpec, attach_user_role, create_role, create_role_request, create_user
from tests.providers import FakeNotificationPort


@pytest.mark.asyncio
async def test_get_time_since_last_reject_uses_passed_request_time(
    dishka_request_container,
) -> None:
    # Given
    service = await dishka_request_container.get(RoleRequestService)
    last_reject = RoleRequest(user_id=1, role_id=1, status=RequestStatus.REJECTED)
    last_reject.updated_at = datetime(2026, 3, 21, 10, 0, 0)
    request_time = datetime(2026, 3, 21, 10, 7, 30)

    # When
    elapsed = service.get_time_since_last_reject(request_time, last_reject)

    # Then
    assert elapsed == timedelta(minutes=7, seconds=30)


@pytest.mark.asyncio
async def test_create_role_request_success_creates_pending_request(
    dishka_request_container,
) -> None:
    # Given
    db = await dishka_request_container.get(AsyncSession)
    service = await dishka_request_container.get(RoleRequestService)
    user = await create_user(db, spec=UserSpec(telegram_id=900_001))
    role = await create_role(db, name="Mentor")
    await db.commit()

    # When
    dto = await service.create_role_request(user_id=user.id, role=role.name)

    # Then
    assert dto.user_id == user.id
    assert dto.role_id == role.id
    assert dto.status == RequestStatus.PENDING


@pytest.mark.asyncio
async def test_create_role_request_raises_when_user_not_found(
    dishka_request_container,
) -> None:
    # Given
    db = await dishka_request_container.get(AsyncSession)
    service = await dishka_request_container.get(RoleRequestService)
    await create_role(db, name="Mentor")
    await db.commit()

    # When / Then
    with pytest.raises(UserNotFoundError):
        await service.create_role_request(user_id=999_001, role="Mentor")


@pytest.mark.asyncio
async def test_create_role_request_raises_when_role_not_found(
    dishka_request_container,
) -> None:
    # Given
    db = await dishka_request_container.get(AsyncSession)
    service = await dishka_request_container.get(RoleRequestService)
    user = await create_user(db, spec=UserSpec(telegram_id=900_002))
    await db.commit()

    # When / Then
    with pytest.raises(RoleNotFoundError):
        await service.create_role_request(user_id=user.id, role="Mentor")


@pytest.mark.asyncio
async def test_create_role_request_raises_when_role_is_already_assigned(
    dishka_request_container,
) -> None:
    # Given
    db = await dishka_request_container.get(AsyncSession)
    service = await dishka_request_container.get(RoleRequestService)
    user = await create_user(db, spec=UserSpec(telegram_id=900_003))
    role = await create_role(db, name="Mentor")
    await attach_user_role(db, user=user, role=role)
    await db.commit()

    # When / Then
    with pytest.raises(RoleAlreadyAssignedError):
        await service.create_role_request(user_id=user.id, role="Mentor")


@pytest.mark.asyncio
async def test_create_role_request_raises_when_pending_request_already_exists(
    dishka_request_container,
) -> None:
    # Given
    db = await dishka_request_container.get(AsyncSession)
    service = await dishka_request_container.get(RoleRequestService)
    user = await create_user(db, spec=UserSpec(telegram_id=900_004))
    role = await create_role(db, name="Mentor")
    await create_role_request(db, spec=RoleRequestSpec(user=user, role=role, status=RequestStatus.PENDING))
    await db.commit()

    # When / Then
    with pytest.raises(RoleRequestAlreadyExistsError):
        await service.create_role_request(user_id=user.id, role="Mentor")


@pytest.mark.asyncio
async def test_check_requesting_user_raises_cooldown_error_with_available_at(
    dishka_request_container,
    settings_obj: BotSettings,
) -> None:
    # Given
    db = await dishka_request_container.get(AsyncSession)
    service = await dishka_request_container.get(RoleRequestService)
    user = await create_user(db, spec=UserSpec(telegram_id=900_005))
    role = await create_role(db, name="Mentor")
    rejected_at = datetime.now() - timedelta(seconds=1)
    await create_role_request(
        db,
        spec=RoleRequestSpec(
            user=user,
            role=role,
            status=RequestStatus.REJECTED,
            updated_at=rejected_at,
        ),
    )
    await db.commit()

    # When / Then
    with pytest.raises(RoleRequestCooldownError) as err:
        await service.check_requesting_user(user_id=user.id, user_role="Mentor")

    assert err.value.available_at == rejected_at + timedelta(minutes=settings_obj.role_request_reject_cooldown_minutes)


@pytest.mark.asyncio
async def test_change_request_status_updates_pending_request(
    dishka_request_container,
) -> None:
    # Given
    db = await dishka_request_container.get(AsyncSession)
    service = await dishka_request_container.get(RoleRequestService)
    notification_service = await dishka_request_container.get(FakeNotificationPort)
    user = await create_user(db, spec=UserSpec(telegram_id=900_006))
    role = await create_role(db, name="Mentor")
    request = await create_role_request(db, spec=RoleRequestSpec(user=user, role=role, status=RequestStatus.PENDING))
    await db.commit()

    # When
    await service.change_request_status(request_id=request.id, new_status=RequestStatus.APPROVED)

    # Then
    stmt = select(RoleRequest).where(RoleRequest.id == request.id)
    updated = (await db.execute(stmt)).scalar_one()
    assert updated.status == RequestStatus.APPROVED
    assert await service.user_repository.has_role(db, user_id=user.id, role_name=role.name)
    assert any(
        item.recipient_id == user.telegram_id and item.message_text == "Ваша заявка на роль Mentor была одобрена."
        for item in notification_service.direct_messages
    )


@pytest.mark.asyncio
async def test_change_request_status_sends_russian_notification_for_rejected_request(
    dishka_request_container,
) -> None:
    # Given
    db = await dishka_request_container.get(AsyncSession)
    service = await dishka_request_container.get(RoleRequestService)
    notification_service = await dishka_request_container.get(FakeNotificationPort)
    user = await create_user(db, spec=UserSpec(telegram_id=900_009))
    role = await create_role(db, name="Admin")
    request = await create_role_request(db, spec=RoleRequestSpec(user=user, role=role, status=RequestStatus.PENDING))
    await db.commit()

    # When
    await service.change_request_status(request_id=request.id, new_status=RequestStatus.REJECTED)

    # Then
    stmt = select(RoleRequest).where(RoleRequest.id == request.id)
    updated = (await db.execute(stmt)).scalar_one()
    assert updated.status == RequestStatus.REJECTED
    assert any(
        item.recipient_id == user.telegram_id and item.message_text == "Ваша заявка на роль Admin была отклонена."
        for item in notification_service.direct_messages
    )


@pytest.mark.asyncio
async def test_change_request_status_raises_when_request_not_found(
    dishka_request_container,
) -> None:
    # Given
    service = await dishka_request_container.get(RoleRequestService)

    # When / Then
    with pytest.raises(RoleRequestNotFoundError):
        await service.change_request_status(request_id=404_404, new_status=RequestStatus.APPROVED)


@pytest.mark.asyncio
async def test_change_request_status_raises_when_request_already_processed(
    dishka_request_container,
) -> None:
    # Given
    db = await dishka_request_container.get(AsyncSession)
    service = await dishka_request_container.get(RoleRequestService)
    user = await create_user(db, spec=UserSpec(telegram_id=900_007))
    role = await create_role(db, name="Mentor")
    request = await create_role_request(db, spec=RoleRequestSpec(user=user, role=role, status=RequestStatus.REJECTED))
    await db.commit()

    # When / Then
    with pytest.raises(RoleRequestAlreadyProcessedError):
        await service.change_request_status(request_id=request.id, new_status=RequestStatus.APPROVED)


@pytest.mark.asyncio
async def test_change_request_status_raises_when_role_was_assigned_before_approve(
    dishka_request_container,
) -> None:
    # Given
    db = await dishka_request_container.get(AsyncSession)
    service = await dishka_request_container.get(RoleRequestService)
    user = await create_user(db, spec=UserSpec(telegram_id=900_008))
    role = await create_role(db, name="Admin")
    repo = UserRepository()
    loaded_user = await repo.get_by_id(db, user.id)
    assert loaded_user is not None
    loaded_user.add_role(role)
    request = await create_role_request(
        db, spec=RoleRequestSpec(user=loaded_user, role=role, status=RequestStatus.PENDING)
    )
    await db.commit()

    # When / Then
    with pytest.raises(RoleAlreadyAssignedError):
        await service.change_request_status(request_id=request.id, new_status=RequestStatus.APPROVED)
