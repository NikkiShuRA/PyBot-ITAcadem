from __future__ import annotations

import pytest

from pybot.core.constants import PointsTypeEnum
from pybot.db.models import User, Valuation
from pybot.domain.exceptions import ZeroPointsAdjustmentError
from pybot.dto.value_objects import Points


def _make_user(*, user_id: int, telegram_id: int) -> User:
    return User(
        id=user_id,
        telegram_id=telegram_id,
        first_name="Test",
    )


def test_create_valuation_uses_points_value_object_and_trims_reason() -> None:
    # Given
    recipient = _make_user(user_id=10, telegram_id=700_010)
    giver = _make_user(user_id=11, telegram_id=700_011)
    points = Points(value=25, point_type=PointsTypeEnum.ACADEMIC)

    # When
    valuation = Valuation.create(
        recipient=recipient,
        giver=giver,
        points=points,
        reason="  Great progress  ",
    )

    # Then
    assert valuation.recipient is recipient
    assert valuation.giver is giver
    assert valuation.recipient_id == recipient.id
    assert valuation.giver_id == giver.id
    assert valuation.points == 25
    assert valuation.points_type is PointsTypeEnum.ACADEMIC
    assert valuation.reason == "Great progress"


def test_create_valuation_rejects_zero_points_value_object() -> None:
    # Given
    recipient = _make_user(user_id=12, telegram_id=700_012)
    giver = _make_user(user_id=13, telegram_id=700_013)
    points = Points(value=0, point_type=PointsTypeEnum.REPUTATION)

    # When / Then
    with pytest.raises(ZeroPointsAdjustmentError):
        Valuation.create(
            recipient=recipient,
            giver=giver,
            points=points,
        )
