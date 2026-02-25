from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncSession

from pybot.core.constants import LevelTypeEnum, RequestStatus
from pybot.db.models import Level, Role, RoleRequest, User, UserLevel, UserRole, Valuation


@dataclass(slots=True)
class UserSpec:
    telegram_id: int
    first_name: str = "Ivan"
    last_name: str = "Petrov"
    patronymic: str | None = "Sergeevich"
    phone_number: str = "+79876543210"
    academic_points: int = 0
    reputation_points: int = 0


@dataclass(slots=True)
class RoleRequestSpec:
    user: User
    role: Role
    status: RequestStatus = RequestStatus.PENDING
    created_at: datetime | None = None
    updated_at: datetime | None = None


@dataclass(slots=True)
class ValuationSpec:
    recipient: User
    giver: User
    points: int
    points_type: LevelTypeEnum
    reason: str | None = None
    created_at: datetime | None = None


async def create_user(
    db: AsyncSession,
    *,
    spec: UserSpec,
) -> User:
    user = User(
        telegram_id=spec.telegram_id,
        first_name=spec.first_name,
        last_name=spec.last_name,
        patronymic=spec.patronymic,
        phone_number=spec.phone_number,
        academic_points=spec.academic_points,
        reputation_points=spec.reputation_points,
    )
    db.add(user)
    await db.flush()
    return user


async def create_role(db: AsyncSession, *, name: str, description: str | None = None) -> Role:
    role = Role(name=name, description=description)
    db.add(role)
    await db.flush()
    return role


async def create_level(
    db: AsyncSession,
    *,
    name: str,
    level_type: LevelTypeEnum,
    required_points: int,
    description: str | None = None,
) -> Level:
    level = Level(
        name=name,
        level_type=level_type,
        required_points=required_points,
        description=description,
    )
    db.add(level)
    await db.flush()
    return level


async def attach_user_level(db: AsyncSession, *, user: User, level: Level) -> UserLevel:
    user_level = UserLevel(user_id=user.id, level_id=level.id, level=level, user=user)
    db.add(user_level)
    await db.flush()
    return user_level


async def attach_user_role(db: AsyncSession, *, user: User, role: Role) -> None:
    user_role = UserRole(user_id=user.id, role_id=role.id)
    db.add(user_role)
    await db.flush()


async def create_role_request(
    db: AsyncSession,
    *,
    spec: RoleRequestSpec,
) -> RoleRequest:
    request = RoleRequest(
        user_id=spec.user.id,
        role_id=spec.role.id,
        status=spec.status,
    )
    if spec.created_at is not None:
        request.created_at = spec.created_at
    if spec.updated_at is not None:
        request.updated_at = spec.updated_at

    db.add(request)
    await db.flush()
    return request


async def create_valuation(
    db: AsyncSession,
    *,
    spec: ValuationSpec,
) -> Valuation:
    valuation = Valuation(
        recipient_id=spec.recipient.id,
        giver_id=spec.giver.id,
        points=spec.points,
        points_type=spec.points_type,
        reason=spec.reason,
    )
    if spec.created_at is not None:
        valuation.created_at = spec.created_at
    db.add(valuation)
    await db.flush()
    return valuation
