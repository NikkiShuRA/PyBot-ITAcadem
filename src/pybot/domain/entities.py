from datetime import date

from pydantic import BaseModel, ConfigDict, Field

from ..core.constants import PointsTypeEnum


class BaseEntityModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)


class LevelEntity(BaseEntityModel):
    """Доменная сущность Уровня."""

    id: int
    name: str
    level_type: PointsTypeEnum
    description: str | None
    required_points: int


class RoleEntity(BaseEntityModel):
    """Доменная сущность Роли (для админов и академических)."""

    id: int
    name: str
    description: str | None = None


class CompetenceEntity(BaseEntityModel):
    """Доменная сущность Компетенции."""

    id: int
    name: str


class AchievementEntity(BaseEntityModel):
    """Доменная сущность Достижения."""

    id: int
    name: str
    icon_url: str | None = None


class UserEntity(BaseEntityModel):
    """Доменная сущность Пользователя."""

    id: int
    first_name: str
    last_name: str | None
    patronymic: str | None
    telegram_id: int
    academic_points: int
    reputation_points: int
    join_date: date

    current_academic_level: LevelEntity | None = None
    current_reputation_level: LevelEntity | None = None

    academic_role: RoleEntity | None = None
    admin_role: RoleEntity | None = None

    competencies: list[CompetenceEntity] = Field(default_factory=list)
    achievements: list[AchievementEntity] = Field(default_factory=list)
