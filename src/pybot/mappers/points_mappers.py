from collections.abc import Sequence

from ..db.models import Valuation
from ..domain import ValuationEntity


async def map_orm_valuation_to_domain(orm_level: Valuation) -> ValuationEntity:
    """Маппит ORM Level объект в доменную LevelEntity."""
    return ValuationEntity.model_validate(orm_level)


async def map_orm_valuations_to_domain(orm_levels: Sequence[Valuation]) -> list[ValuationEntity]:
    """Маппит список ORM Level объектов в список доменных LevelEntity."""
    return [await map_orm_valuation_to_domain(level) for level in orm_levels]
