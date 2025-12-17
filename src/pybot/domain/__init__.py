from .user import UserEntity as UserEntity
from .level import LevelEntity as LevelEntity
from .role import RoleEntity as RoleEntity
from .competence import CompetenceEntity as CompetenceEntity
from .achievement import AchievementEntity as AchievementEntity
from .attachment import AttachmentEntity as AttachmentEntity
from .comment import CommentEntity as CommentEntity
from .task import TaskEntity as TaskEntity
from .project import ProjectEntity as ProjectEntity


UserEntity.model_rebuild()
LevelEntity.model_rebuild()
ProjectEntity.model_rebuild()
TaskEntity.model_rebuild()
AchievementEntity.model_rebuild()
RoleEntity.model_rebuild()
CompetenceEntity.model_rebuild()
CommentEntity.model_rebuild()
AttachmentEntity.model_rebuild()
