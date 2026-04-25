from __future__ import annotations

from collections.abc import Sequence

from ..db.models import Competence
from ..dto import CompetenceReadDTO


async def map_orm_competence_to_competence_read_dto(orm_competence: Competence) -> CompetenceReadDTO:
    """Преобразует ORM-модель компетенции в DTO для чтения.

    Args:
        orm_competence: Исходная ORM-модель компетенции.

    Returns:
        CompetenceReadDTO: Валидированный DTO с данными компетенции.
    """
    return CompetenceReadDTO.model_validate(orm_competence)


async def map_orm_competencies_to_competence_read_dtos(
    orm_competencies: Sequence[Competence],
) -> list[CompetenceReadDTO]:
    """Преобразует список ORM-моделей компетенций в список DTO.

    Args:
        orm_competencies: Последовательность ORM-моделей компетенций.

    Returns:
        list[CompetenceReadDTO]: Список DTO для чтения.
    """
    return [await map_orm_competence_to_competence_read_dto(orm_competence) for orm_competence in orm_competencies]
