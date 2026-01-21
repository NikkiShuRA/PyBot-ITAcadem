from .user import UserEntity as UserEntity
from .level import LevelEntity as LevelEntity
from .role import RoleEntity as RoleEntity
from .competence import CompetenceEntity as CompetenceEntity
from .achievement import AchievementEntity as AchievementEntity
from .task import TaskEntity as TaskEntity
from .valuation import ValuationEntity as ValuationEntity
from .value_objects import Points as Points
from .factories import default_academic_points, default_reputation_points

UserEntity.model_rebuild()
LevelEntity.model_rebuild()
TaskEntity.model_rebuild()
AchievementEntity.model_rebuild()
RoleEntity.model_rebuild()
CompetenceEntity.model_rebuild()
ValuationEntity.model_rebuild()
