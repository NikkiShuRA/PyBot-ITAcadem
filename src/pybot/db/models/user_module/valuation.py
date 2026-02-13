from __future__ import annotations

from datetime import UTC, datetime

from sqlalchemy import BigInteger, DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ....core.constants import LevelTypeEnum
from ....dto.value_objects import Points
from ...base_class import Base
from .user import User


class Valuation(Base):
    __tablename__ = "valuations"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    recipient_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )
    giver_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )
    reason: Mapped[str | None] = mapped_column(Text)
    points: Mapped[int] = mapped_column(Integer, nullable=False)
    points_type: Mapped[LevelTypeEnum] = mapped_column(
        String(50),
        nullable=False,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=False),  # SQLite не поддерживает timezone
        nullable=False,
        server_default=func.now(),
    )
    recipient: Mapped[User] = relationship(
        "User",
        foreign_keys=[recipient_id],
        back_populates="valuations_received",
    )
    giver: Mapped[User] = relationship(
        "User",
        foreign_keys=[giver_id],
        back_populates="valuations_given",
    )

    def __repr__(self) -> str:
        return (
            f"<Valuation(id={self.id}, "
            f"recipient={self.recipient_id}, "
            f"giver={self.giver_id}, "
            f"points={self.points} {self.points_type.value}, "
            f"created={self.created_at.isoformat()[:19]})>"
        )

    def __str__(self) -> str:
        return (
            f"Valuation of {self.points} {self.points_type.value} points "
            f"from User {self.giver_id} to User {self.recipient_id} "
            f"on {self.created_at}. Reason: {self.reason or 'No reason provided.'}"
        )

    @classmethod
    def create(
        cls,
        recipient: User,
        giver: User,
        points: int,
        point_type: LevelTypeEnum,
        reason: str | None = None,
    ) -> Valuation:
        """
        Создает запись о начислении.
        Гарантирует валидацию на уровне создания.
        """
        if points == 0:
            raise ValueError("Нельзя создать запись с 0 баллов")

        clean_reason = reason.strip() if reason else None

        return cls(
            recipient_id=recipient.id,
            giver_id=giver.id,
            points=points,
            points_type=point_type,
            reason=clean_reason,
            created_at=datetime.now(UTC),
            recipient=recipient,
            giver=giver,
        )

    @hybrid_property
    def points_vo(self) -> Points:
        return Points(value=self.points, point_type=self.points_type)

    @points_vo.expression  # ty:ignore[invalid-argument-type]
    def points_vo(cls) -> int:  # noqa: N805
        return cls.points
