from ..base_class import Base

# Shared (общие) модели
from .achievement import Achievement


# Доменные подпакеты
from .user_module import (
    User,
    UserLevel,
    UserActivityStatus,
    AdminRole,
    AcademicRole,
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

__all__ = [
    "Base",
    # shared
    "Achievement",
    # user_module
    "User",
    "UserActivityStatus",
    "AdminRole",
    "AcademicRole",
    "Level",
    "UserLevel",
    "Competence",
    "UserCompetence",
    "UserAchievement",
    "Valuation",
    # task_module
    "Task",
    "TaskSolution",
    "TaskSolutionStatus",
]
