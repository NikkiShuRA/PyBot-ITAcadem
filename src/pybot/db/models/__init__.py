from ..base_class import Base


from .user_module import (
    User,
    UserActivity,
)

from .task_module import (
    Task,
    TaskSolution,
    TaskSolutionStatus,
)

from .role_module import (
    Permission,
    RoleSystem,
    Role,
    RolePermission,
    UserRole,
    RoleEvent,
)

from .level_module import (
    Level,
    LevelSystem,
    PointEvent,
    PointReasonType,
    UserLevelState,
)

__all__ = [
    "Base",

    # user_module
    "User",
    "UserActivity",

    # task_module
    "Task",
    "TaskSolution",
    "TaskSolutionStatus",

    # role_module
    "Permission",
    "RoleSystem",
    "Role",
    "RolePermission",
    "UserRole",
    "RoleEvent",

    # level_module
    "Level",
    "LevelSystem",
    "PointEvent",
    "PointReasonType",
    "UserLevelState",
]
