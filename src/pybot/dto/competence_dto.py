from __future__ import annotations

from pydantic import Field, field_validator

from .base_dto import BaseDTO


class CompetenceReadDTO(BaseDTO):
    id: int = Field(..., gt=0)
    name: str = Field(..., min_length=1, max_length=100)
    description: str | None = Field(default=None, max_length=500)


class CompetenceByIdDTO(BaseDTO):
    competence_id: int = Field(..., gt=0)


class CompetenceCreateDTO(BaseDTO):
    name: str = Field(..., min_length=1, max_length=100)
    description: str | None = Field(default=None, max_length=500)

    @field_validator("name")
    @classmethod
    def normalize_name(cls, value: str) -> str:
        normalized = value.strip()
        if not normalized:
            raise ValueError("Competence name cannot be empty")
        return normalized

    @field_validator("description")
    @classmethod
    def normalize_description(cls, value: str | None) -> str | None:
        if value is None:
            return None
        normalized = value.strip()
        return normalized or None


class CompetenceIdsDTO(BaseDTO):
    competence_ids: list[int] = Field(..., min_length=1)

    @field_validator("competence_ids")
    @classmethod
    def validate_competence_ids(cls, value: list[int]) -> list[int]:
        if any(competence_id <= 0 for competence_id in value):
            raise ValueError("All competence ids must be positive integers")
        return sorted(set(value))


class CompetenceUpdateDTO(BaseDTO):
    competence_id: int = Field(..., gt=0)
    name: str = Field(..., min_length=1, max_length=100)
    description: str | None = Field(default=None, max_length=500)

    @field_validator("name")
    @classmethod
    def normalize_name(cls, value: str) -> str:
        normalized = value.strip()
        if not normalized:
            raise ValueError("Competence name cannot be empty")
        return normalized

    @field_validator("description")
    @classmethod
    def normalize_description(cls, value: str | None) -> str | None:
        if value is None:
            return None
        normalized = value.strip()
        return normalized or None
