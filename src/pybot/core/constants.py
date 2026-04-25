from enum import StrEnum


class PointsTypeEnum(StrEnum):
    """Available point balance types.

    Attributes:
        ACADEMIC: Academic progress points.
        REPUTATION: Reputation points for community contribution.
    """

    ACADEMIC = "academic"
    REPUTATION = "reputation"


class RoleEventOperandEnum(StrEnum):
    """Supported role event operations.

    Attributes:
        ADD: Add a role to a user.
        DELETE: Remove a role from a user.
        REPLACE: Replace a user's current roles.
    """

    ADD = "add"
    DELETE = "delete"
    REPLACE = "replace"


class RoleEnum(StrEnum):
    """Canonical user roles used by access-control logic.

    Attributes:
        STUDENT: Base student role.
        MENTOR: Mentor role with elevated educational permissions.
        ADMIN: Administrator role with privileged management permissions.
    """

    STUDENT = "Student"
    MENTOR = "Mentor"
    ADMIN = "Admin"


class RequestStatus(StrEnum):
    """Lifecycle statuses for user-initiated requests.

    Attributes:
        PENDING: Request is awaiting a decision.
        APPROVED: Request has been approved.
        REJECTED: Request has been rejected.
        CANCELED: Request has been canceled by the initiator or system.
    """

    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    CANCELED = "canceled"


class TaskScheduleKind(StrEnum):
    """Supported scheduling modes for background tasks.

    Attributes:
        IMMEDIATE: Run the task without a schedule delay.
        AT: Run the task once at a specific time.
        INTERVAL: Run the task repeatedly with a fixed interval.
        CRON: Run the task according to a cron expression.
    """

    IMMEDIATE = "immediate"
    AT = "at"
    INTERVAL = "interval"
    CRON = "cron"


class RolePolicyKey(StrEnum):
    """Configuration keys for role-based policies.

    Attributes:
        BROADCAST: Settings key that defines roles allowed to send broadcasts.
    """

    BROADCAST = "broadcast_allowed_roles"
