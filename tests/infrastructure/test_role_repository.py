from __future__ import annotations

import pytest

from pybot.infrastructure.role_repository import RoleRepository
from tests.factories import create_role


@pytest.mark.asyncio
async def test_find_role_by_name_returns_role_when_present(db_session) -> None:
    # Given
    repo = RoleRepository()
    role = await create_role(db_session, name="Mentor")
    await db_session.commit()

    # When
    found = await repo.find_role_by_name(db_session, role.name)

    # Then
    assert found is not None
    assert found.id == role.id


@pytest.mark.asyncio
async def test_find_role_by_name_returns_none_when_absent(db_session) -> None:
    # Given
    repo = RoleRepository()

    # When
    found = await repo.find_role_by_name(db_session, "GhostRole")

    # Then
    assert found is None


@pytest.mark.asyncio
async def test_find_all_roles_returns_roles_sorted_by_name(db_session) -> None:
    # Given
    repo = RoleRepository()
    await create_role(db_session, name="Student")
    await create_role(db_session, name="Admin")
    await create_role(db_session, name="Mentor")
    await db_session.commit()

    # When
    found_roles = await repo.find_all_roles(db_session)

    # Then
    assert [role.name for role in found_roles] == ["Admin", "Mentor", "Student"]
