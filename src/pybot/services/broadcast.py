import asyncio
import random

from sqlalchemy.ext.asyncio import AsyncSession

from ..core import logger
from ..db.models import User
from ..infrastructure.user_repository import UserRepository
from .ports import NotificationPort


class BroadcastService:
    def __init__(
        self, db: AsyncSession, user_repository: UserRepository, notification_service: NotificationPort
    ) -> None:
        self.db: AsyncSession = db
        self.user_repository: UserRepository = user_repository
        self.notification_service: NotificationPort = notification_service

    async def _send_messages_in_bulk(self, users: list[User], message: str, bulk_size: int = 20) -> None:
        jitter_range = range(50, 101)
        for i in range(0, len(users), bulk_size):
            bulk_users = users[i : i + bulk_size]
            awaitables = []
            for user in bulk_users:
                awaitables.append(self.notification_service.send_message(user.telegram_id, message))
            await asyncio.gather(*awaitables)
            if i + bulk_size < len(users):
                jitter = random.choice(jitter_range)  # noqa: S311
                await asyncio.sleep(jitter / 1000)

    async def broadcast_for_all(self, message: str) -> None:
        users = await self.user_repository.get_all_users(self.db)
        await self._send_messages_in_bulk(users, message)
        logger.info(f"Broadcasted message to {len(users)} users")

    async def broadcast_for_users_with_role(self, role_name: str, message: str) -> None:
        users = await self.user_repository.get_all_users_with_role(self.db, role_name)
        await self._send_messages_in_bulk(users, message)
        logger.info(f"Broadcasted message to {len(users)} users with role {role_name}")
