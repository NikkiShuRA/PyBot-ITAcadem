from __future__ import annotations

from collections.abc import Sequence

from ..db.models import Competence
from ..dto import CompetenceReadDTO


async def map_orm_competence_to_competence_read_dto(orm_competence: Competence) -> CompetenceReadDTO:
    return CompetenceReadDTO.model_validate(orm_competence)


async def map_orm_competencies_to_competence_read_dtos(
    orm_competencies: Sequence[Competence],
) -> list[CompetenceReadDTO]:
    return [await map_orm_competence_to_competence_read_dto(orm_competence) for orm_competence in orm_competencies]
