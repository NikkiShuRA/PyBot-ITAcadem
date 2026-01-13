from ..core.constants import PointsTypeEnum
from .value_objects import Points


def default_academic_points() -> Points:
    """Дефолтные академические баллы (value=0, type=ACADEMIC)."""
    return Points(value=0, point_type=PointsTypeEnum.ACADEMIC)


def default_reputation_points() -> Points:
    """Дефолтные репутационные баллы (value=0, type=REPUTATION)."""
    return Points(value=0, point_type=PointsTypeEnum.REPUTATION)
