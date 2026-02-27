from __future__ import annotations

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from pybot.infrastructure.competence_repository import CompetenceRepository
from tests.factories import create_competence


@pytest.mark.asyncio
async def test_get_by_names_returns_matching_competencies_case_insensitive(dishka_request_container) -> None:
    db = await dishka_request_container.get(AsyncSession)
    repository = await dishka_request_container.get(CompetenceRepository)
    await create_competence(db, name="Python")
    await create_competence(db, name="SQL")
    await create_competence(db, name="Go")
    await db.commit()

    competencies = await repository.get_by_names(db, ["python", "SQL"])

    assert [competence.name for competence in competencies] == ["Python", "SQL"]


@pytest.mark.asyncio
async def test_get_by_names_deduplicates_and_ignores_empty_values(dishka_request_container) -> None:
    db = await dishka_request_container.get(AsyncSession)
    repository = await dishka_request_container.get(CompetenceRepository)
    await create_competence(db, name="Docker")
    await db.commit()

    competencies = await repository.get_by_names(db, [" docker ", "DOCKER", ""])

    assert [competence.name for competence in competencies] == ["Docker"]


@pytest.mark.asyncio
async def test_get_by_names_returns_empty_for_empty_input(dishka_request_container) -> None:
    db = await dishka_request_container.get(AsyncSession)
    repository = await dishka_request_container.get(CompetenceRepository)

    competencies = await repository.get_by_names(db, [])

    assert competencies == []
