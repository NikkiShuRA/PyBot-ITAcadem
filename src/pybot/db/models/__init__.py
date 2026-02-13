from ..base_class import Base

# Shared (общие) модели
from .achievement import Achievement


# Доменные подпакеты
from .user_module import (
    User,
    UserLevel,
    UserActivityStatus,
    Level,
    Competence,
    UserCompetence,
    UserAchievement,
    Valuation,
)

from .task_module import (
    Task,
    TaskSolution,
    TaskSolutionStatus,
)

from .role_module import (
    Role,
    UserRole,
    RoleEvent,
    RoleRequest,
)

__all__ = [
    "Base",
    # shared
    "Achievement",
    # user_module
    "User",
    "UserActivityStatus",
    "Level",
    "UserLevel",
    "Competence",
    "UserCompetence",
    "UserAchievement",
    "Valuation",
    # role_module
    "Role",
    "UserRole",
    "RoleEvent",
    # task_module
    "Task",
    "TaskSolution",
    "TaskSolutionStatus",
]
