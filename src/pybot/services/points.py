from sqlalchemy.ext.asyncio import AsyncSession

from ..core import logger
from ..db.models import PointsTransaction, Valuation
from ..domain.exceptions import UserNotFoundError
from ..domain.services.level_calculator import LevelCalculator
from ..dto import AdjustUserPointsDTO, UserReadDTO
from ..infrastructure.level_repository import LevelRepository
from ..infrastructure.points_transaction_repository import PointsTransactionRepository
from ..infrastructure.user_repository import UserRepository
from ..mappers.user_mappers import map_orm_user_to_user_read_dto


class PointsService:
    def __init__(
        self,
        db: AsyncSession,
        level_calculator: LevelCalculator,
        user_repository: UserRepository,
        level_repository: LevelRepository,
        points_transaction_repository: PointsTransactionRepository,
    ) -> None:
        self.db: AsyncSession = db
        self.level_calculator: LevelCalculator = level_calculator
        self.user_repository: UserRepository = user_repository
        self.level_repository: LevelRepository = level_repository
        self.points_transaction_repository: PointsTransactionRepository = points_transaction_repository

    async def change_points(self, dto: AdjustUserPointsDTO) -> UserReadDTO:
        try:
            user = await self.user_repository.get_by_id(self.db, dto.recipient_id)
        except UserNotFoundError as err:
            raise UserNotFoundError(user_id=dto.recipient_id) from err

        all_levels = await self.level_repository.find_all_by_type(self.db, dto.points.point_type)
        actual_delta, new_score = user.change_user_points(dto.points.value, dto.points.point_type)
        new_level = self.level_calculator.calculate_level(new_score, all_levels)

        if new_level:
            user.change_user_level(new_level.id, dto.points.point_type)
        else:
            logger.info("Пользователь достиг максимального уровня")

        try:
            giver_orm = await self.user_repository.get_by_id(self.db, dto.giver_id)
        except UserNotFoundError as err:
            raise UserNotFoundError(user_id=dto.giver_id) from err

        valuation = Valuation.create(
            recipient=user,
            giver=giver_orm,
            points=dto.points,
            reason=dto.reason,
        )
        points_transaction = PointsTransaction.create(
            recipient_id=user.id,
            giver_id=giver_orm.id,
            amount=actual_delta,
            points_type=dto.points.point_type,
        )

        self.db.add(valuation)
        await self.points_transaction_repository.add(self.db, points_transaction)
        self.db.add(user)
        await self.db.commit()

        return await map_orm_user_to_user_read_dto(user)
