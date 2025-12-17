from ..base_class import Base

# Shared (общие) модели
from .attachment_module import (
    Attachment,
    AttachmentTypes
)


# Доменные подпакеты
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

__all__ = [
    "Base",

    # shared
    "AttachmentTypes",
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
]
