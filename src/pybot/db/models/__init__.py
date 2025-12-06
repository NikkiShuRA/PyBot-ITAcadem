from ..base_class import Base

# Shared (общие) модели
from .achievement import Achievement

from .attachments_types import AttachmentsType
from .attachments import Attachment

from .comment_answers import CommentAnswer
from .comment_attachments import CommentAttachment
from .comments import Comment

# Доменные подпакеты
from .user_module import (
    User,
    UserActivityStatus,
    AdminRole,
    AcademicRole,
    Level,
    Competence,
    UserCompetence,
    UserAchievement,
    Valuation,
)

from .project_module import (
    Project,
    ProjectStatus,
    ProjectMember,
    ProjectMemberRole,
    ProjectAttachment,
    ProjectAchievement,
    ProjectComment,
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
    "AttachmentsType",
    "Attachment",
    "CommentAnswer",
    "CommentAttachment",
    "Comment",
    # user_module
    "User",
    "UserActivityStatus",
    "AdminRole",
    "AcademicRole",
    "Level",
    "Competence",
    "UserCompetence",
    "UserAchievement",
    "Valuation",
    # project_module
    "Project",
    "ProjectStatus",
    "ProjectMember",
    "ProjectMemberRole",
    "ProjectAttachment",
    "ProjectAchievement",
    "ProjectComment",
    # task_module
    "Task",
    "TaskAttachment",
    "TaskComment",
    "TaskSolution",
    "TaskSolutionStatus",
    "TaskSolutionComment",
]
