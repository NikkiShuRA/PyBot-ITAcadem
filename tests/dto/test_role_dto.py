import pytest
from pydantic import ValidationError

from pybot.dto import RoleByIdDTO, RoleIdsDTO, RoleReadDTO


def test_role_read_dto_accepts_model_fields() -> None:
    dto = RoleReadDTO(id=1, name="Mentor", description="Helps students")

    assert dto.id == 1
    assert dto.name == "Mentor"
    assert dto.description == "Helps students"


def test_role_by_id_dto_rejects_non_positive_id() -> None:
    with pytest.raises(ValidationError, match="greater than 0"):
        RoleByIdDTO(role_id=0)


def test_role_ids_dto_sorts_and_deduplicates_ids() -> None:
    dto = RoleIdsDTO(role_ids=[3, 1, 3, 2])

    assert dto.role_ids == [1, 2, 3]


def test_role_ids_dto_rejects_non_positive_id() -> None:
    with pytest.raises(ValidationError, match="positive integers"):
        RoleIdsDTO(role_ids=[1, 0, 2])
