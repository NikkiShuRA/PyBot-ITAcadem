from db_class.base_class import Base

# Shared (общие) модели
from db_class.models.achievement import Achievement

from db_class.models.attachments_types import AttachmentsType
from db_class.models.attachments import Attachment

from db_class.models.comment_answers import CommentAnswer
from db_class.models.comment_attachments import CommentAttachment
from db_class.models.comments import Comment

# Доменные подпакеты
from db_class.models.user_module import (
    User,
    UserActivityStatus,
    AdminRole,
    AcademicRole,
    Level,
    Competence,
    UserCompetence,
    UserAchievement,
    UserTask,
    Valuation,
)

from db_class.models.project_module import (
    Project,
    ProjectStatus,
    ProjectMember,
    ProjectMemberRole,
    ProjectAttachment,
    ProjectAchievement,
    ProjectComment,
)

from db_class.models.task_module import (
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
    "UserTask",
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
