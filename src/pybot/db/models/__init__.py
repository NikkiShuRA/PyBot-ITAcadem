from ..base_class import Base


from .attachment_module import (
    Attachment,
    AttachmentType
)

from .user_module import (
    User,
    UserActivity
)

from .task_module import (
    Task,
    TaskAttachment,
    TaskSolution,
    TaskSolutionAttachment,
    TaskSolutionStatus
)

from .role_module import (
    Permission,
    RoleSystem,
    Role,
    RolePermission,
    UserRole,
    RoleEvent
)

from .level_module import (
    Level,
    LevelSystem,
    PointEvent,
    PointReasonType,
    UserLevelState
)

__all__ = [
    "Base",

    # attachment_module
    "AttachmentType",
    "Attachment",

    # user_module
    "User",
    "UserActivity",

    # task_module
    "Task",
    "TaskAttachment",
    "TaskSolution",
    "TaskSolutionAttachment",
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
    "UserLevelState"
]
