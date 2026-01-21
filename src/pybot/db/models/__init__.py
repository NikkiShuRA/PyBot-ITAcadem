from ..base_class import Base

# Shared (общие) модели
from .achievement import Achievement

from .comment_answers import CommentAnswer
from .comment_attachments import CommentAttachment
from .comments import Comment

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
    TaskAttachment,
    TaskComment,
    TaskSolution,
    TaskSolutionStatus,
    TaskSolutionComment,
)

__all__ = [
    "Base",
    # shared
    "Achievement",
    "CommentAnswer",
    "CommentAttachment",
    "Comment",
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
    "TaskAttachment",
    "TaskComment",
    "TaskSolution",
    "TaskSolutionStatus",
    "TaskSolutionComment",
]
