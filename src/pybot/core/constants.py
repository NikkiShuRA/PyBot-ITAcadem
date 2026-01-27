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
