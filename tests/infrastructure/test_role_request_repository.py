from __future__ import annotations

from datetime import datetime, timedelta

import pytest

from pybot.core.constants import RequestStatus
from pybot.infrastructure.roles.role_request_repository import RoleRequestRepository
from tests.factories import RoleRequestSpec, UserSpec, create_role, create_role_request, create_user


@pytest.mark.asyncio
async def test_get_recent_active_request_returns_pending_for_user(db_session) -> None:
    # Given
    repo = RoleRequestRepository()
    user = await create_user(db_session, spec=UserSpec(telegram_id=510_001))
    role = await create_role(db_session, name="Mentor")
    request = await create_role_request(
        db_session, spec=RoleRequestSpec(user=user, role=role, status=RequestStatus.PENDING)
    )
    await db_session.commit()

    # When
    found = await repo.get_recent_active_request(db_session, user.id)

    # Then
    assert found is not None
    assert found.id == request.id
    assert found.status == RequestStatus.PENDING


@pytest.mark.asyncio
async def test_get_recent_active_request_returns_none_when_absent(db_session) -> None:
    # Given
    repo = RoleRequestRepository()
    user = await create_user(db_session, spec=UserSpec(telegram_id=510_002))
    role = await create_role(db_session, name="Mentor")
    await create_role_request(db_session, spec=RoleRequestSpec(user=user, role=role, status=RequestStatus.REJECTED))
    await db_session.commit()

    # When
    found = await repo.get_recent_active_request(db_session, user.id)

    # Then
    assert found is None


@pytest.mark.asyncio
async def test_get_last_rejected_request_returns_newest_record_by_created_at_desc(db_session) -> None:
    # Given
    repo = RoleRequestRepository()
    user = await create_user(db_session, spec=UserSpec(telegram_id=510_003))
    role = await create_role(db_session, name="Mentor")
    await create_role_request(
        db_session,
        spec=RoleRequestSpec(
            user=user,
            role=role,
            status=RequestStatus.REJECTED,
            created_at=datetime.now() - timedelta(days=2),
        ),
    )
    recent_request = await create_role_request(
        db_session,
        spec=RoleRequestSpec(
            user=user,
            role=role,
            status=RequestStatus.REJECTED,
            created_at=datetime.now() - timedelta(days=1),
        ),
    )
    await db_session.commit()

    # When
    found = await repo.get_last_rejected_request(db_session, user.id)

    # Then
    assert found is not None
    assert found.id == recent_request.id


@pytest.mark.asyncio
async def test_get_all_role_requests_returns_all_rows(db_session) -> None:
    # Given
    repo = RoleRequestRepository()
    user1 = await create_user(db_session, spec=UserSpec(telegram_id=510_004))
    user2 = await create_user(db_session, spec=UserSpec(telegram_id=510_005))
    role = await create_role(db_session, name="Admin")
    await create_role_request(db_session, spec=RoleRequestSpec(user=user1, role=role, status=RequestStatus.PENDING))
    await create_role_request(db_session, spec=RoleRequestSpec(user=user2, role=role, status=RequestStatus.REJECTED))
    await db_session.commit()

    # When
    all_requests = await repo.get_all_role_requests(db_session)

    # Then
    assert len(all_requests) == 2
