from enum import StrEnum


class PointsTypeEnum(StrEnum):
    ACADEMIC = "academic"
    REPUTATION = "reputation"


class RoleEventOperandEnum(StrEnum):
    ADD = "add"
    DELETE = "delete"
    REPLACE = "replace"


class RoleEnum(StrEnum):
    STUDENT = "Student"
    MENTOR = "Mentor"
    ADMIN = "Admin"


class RequestStatus(StrEnum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    CANCELED = "canceled"


class TaskScheduleKind(StrEnum):
    IMMEDIATE = "immediate"
    AT = "at"
    INTERVAL = "interval"
    CRON = "cron"


class RolePolicyKey(StrEnum):
    BROADCAST = "broadcast_allowed_roles"
