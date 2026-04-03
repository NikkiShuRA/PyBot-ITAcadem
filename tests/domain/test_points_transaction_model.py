from __future__ import annotations

from pybot.core.constants import PointsTypeEnum
from pybot.db.models import PointsTransaction, User


def _make_user(*, user_id: int, telegram_id: int) -> User:
    return User(
        id=user_id,
        telegram_id=telegram_id,
        first_name="Test",
    )


def test_create_points_transaction_uses_given_values() -> None:
    # Given
    recipient = _make_user(user_id=20, telegram_id=700_020)
    giver = _make_user(user_id=21, telegram_id=700_021)

    # When
    points_transaction = PointsTransaction.create(
        recipient_id=recipient.id,
        giver_id=giver.id,
        amount=15,
        points_type=PointsTypeEnum.ACADEMIC,
    )

    # Then
    assert points_transaction.recipient_id == recipient.id
    assert points_transaction.giver_id == giver.id
    assert points_transaction.amount == 15
    assert points_transaction.points_type is PointsTypeEnum.ACADEMIC
    assert points_transaction.created_at is not None


def test_create_points_transaction_allows_nullable_giver() -> None:
    # When
    points_transaction = PointsTransaction.create(
        recipient_id=22,
        giver_id=None,
        amount=-5,
        points_type=PointsTypeEnum.REPUTATION,
    )

    # Then
    assert points_transaction.giver_id is None
    assert points_transaction.amount == -5
    assert points_transaction.points_type is PointsTypeEnum.REPUTATION
