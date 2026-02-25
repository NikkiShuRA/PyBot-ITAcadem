from __future__ import annotations

from datetime import datetime, timedelta

import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from pybot.core.constants import RequestStatus
from pybot.db.models import RoleRequest
from pybot.domain.exceptions import (
    RoleAlreadyAssignedError,
    RoleNotFoundError,
    RoleRequestAlreadyExistsError,
    RoleRequestAlreadyProcessedError,
    RoleRequestNotFoundError,
    UserNotFoundError,
)
from pybot.services.role_request import RoleRequestService
from tests.factories import RoleRequestSpec, UserSpec, attach_user_role, create_role, create_role_request, create_user


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
async def test_check_requesting_user_returns_false_on_recent_reject_cooldown(
    dishka_request_container,
) -> None:
    # Given
    db = await dishka_request_container.get(AsyncSession)
    service = await dishka_request_container.get(RoleRequestService)
    user = await create_user(db, spec=UserSpec(telegram_id=900_005))
    role = await create_role(db, name="Mentor")
    await create_role_request(
        db,
        spec=RoleRequestSpec(
            user=user,
            role=role,
            status=RequestStatus.REJECTED,
            updated_at=datetime.now() - timedelta(seconds=1),
        ),
    )
    await db.commit()

    # When
    is_allowed = await service.check_requesting_user(user_id=user.id, user_role="Mentor")

    # Then
    assert is_allowed is False


@pytest.mark.asyncio
async def test_change_request_status_updates_pending_request(
    dishka_request_container,
) -> None:
    # Given
    db = await dishka_request_container.get(AsyncSession)
    service = await dishka_request_container.get(RoleRequestService)
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
