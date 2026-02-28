from __future__ import annotations

import asyncio
import random
from collections.abc import Sequence
from dataclasses import dataclass

from sqlalchemy.ext.asyncio import AsyncSession
from tenacity import AsyncRetrying, RetryCallState, retry_if_exception_type, stop_after_attempt

from ..core import logger
from ..core.config import settings
from ..db.models import User
from ..infrastructure.user_repository import UserRepository
from .ports import NotificationPermanentError, NotificationPort, NotificationTemporaryError


class BroadcastAlreadyRunningError(RuntimeError):
    """Raised when another broadcast is already in progress."""


@dataclass(slots=True)
class BroadcastResult:
    attempted: int = 0
    sent: int = 0
    failed_temporary: int = 0
    failed_permanent: int = 0
    skipped_invalid_user: int = 0


class BroadcastService:
    _broadcast_lock: asyncio.Lock | None = None
    _broadcast_lock_loop: asyncio.AbstractEventLoop | None = None

    def __init__(
        self,
        db: AsyncSession,
        user_repository: UserRepository,
        notification_service: NotificationPort,
    ) -> None:
        self.db = db
        self.user_repository = user_repository
        self.notification_service = notification_service

    @classmethod
    def _get_broadcast_lock(cls) -> asyncio.Lock:
        running_loop = asyncio.get_running_loop()
        if cls._broadcast_lock is None or cls._broadcast_lock_loop is not running_loop:
            cls._broadcast_lock = asyncio.Lock()
            cls._broadcast_lock_loop = running_loop
        return cls._broadcast_lock

    def _normalize_message(self, message: str) -> str:
        normalized = message.strip()
        if not normalized:
            raise ValueError("message must not be empty")

        max_length_with_suffix = min(settings.broadcast_max_text_length + 3, 4096)
        if len(normalized) <= max_length_with_suffix:
            return normalized

        # Keep final message length within configured limit while preserving
        # user feedback that text was truncated.
        return f"{normalized[: max_length_with_suffix - 3]}..."

    def _normalize_role(self, role_name: str) -> str:
        normalized = role_name.strip()
        if not normalized:
            raise ValueError("role_name must not be empty")
        return normalized

    def _normalize_competence_id(self, competence_id: int) -> int:
        if competence_id <= 0:
            raise ValueError("competence_id must be positive")
        return competence_id

    def _wait_for_retry(self, retry_state: RetryCallState) -> float:
        outcome = retry_state.outcome
        if outcome is not None:
            exception = outcome.exception()
            if isinstance(exception, NotificationTemporaryError) and exception.retry_after_seconds is not None:
                return max(0.0, exception.retry_after_seconds)

        exponential = min(float(settings.broadcast_retry_max_wait_s), float(2 ** (retry_state.attempt_number - 1)))
        jitter = random.uniform(0.0, 1.0)  # noqa: S311
        return min(float(settings.broadcast_retry_max_wait_s), exponential + jitter)

    def _batch_pause_seconds(self) -> float:
        jitter_ms = random.randint(settings.broadcast_jitter_min_ms, settings.broadcast_jitter_max_ms)  # noqa: S311
        return (settings.broadcast_batch_pause_ms + jitter_ms) / 1000

    async def _send_with_retry(self, user_id: int, message: str) -> None:
        retrying = AsyncRetrying(
            stop=stop_after_attempt(settings.broadcast_retry_attempts),
            retry=retry_if_exception_type(NotificationTemporaryError),
            wait=self._wait_for_retry,
            reraise=True,
        )
        async for attempt in retrying:
            with attempt:
                await self.notification_service.send_message(user_id=user_id, message_text=message)

    async def _send_one_user(self, user_id: int, message: str, result: BroadcastResult) -> None:
        result.attempted += 1
        if user_id <= 0:
            result.skipped_invalid_user += 1
            logger.warning("Broadcast skipped invalid telegram user id: {user_id}", user_id=user_id)
            return

        try:
            await self._send_with_retry(user_id=user_id, message=message)
        except NotificationTemporaryError:
            result.failed_temporary += 1
            logger.warning("Broadcast temporary delivery failure for user_id={user_id}", user_id=user_id)
        except NotificationPermanentError:
            result.failed_permanent += 1
            logger.warning("Broadcast permanent delivery failure for user_id={user_id}", user_id=user_id)
        except Exception:
            result.failed_permanent += 1
            logger.exception("Broadcast unexpected delivery failure for user_id={user_id}", user_id=user_id)
        else:
            result.sent += 1

    async def _send_batch(self, users: Sequence[User], message: str, result: BroadcastResult) -> None:
        semaphore = asyncio.Semaphore(settings.broadcast_max_concurrency)

        async def worker(user: User) -> None:
            async with semaphore:
                await self._send_one_user(user.telegram_id, message, result)

        worker_tasks = [worker(user) for user in users]
        outcomes = await asyncio.gather(*worker_tasks, return_exceptions=True)
        for outcome in outcomes:
            if isinstance(outcome, Exception):
                logger.exception("Broadcast worker failed outside guarded flow: {error}", error=str(outcome))

    async def _broadcast_users(self, users: Sequence[User], message: str) -> BroadcastResult:
        result = BroadcastResult()
        bulk_size = settings.broadcast_bulk_size

        for index in range(0, len(users), bulk_size):
            batch_users = users[index : index + bulk_size]
            await self._send_batch(batch_users, message, result)
            if index + bulk_size < len(users):
                await asyncio.sleep(self._batch_pause_seconds())

        return result

    async def broadcast_for_all(self, message: str) -> BroadcastResult:
        broadcast_lock = self._get_broadcast_lock()
        if broadcast_lock.locked():
            raise BroadcastAlreadyRunningError("Broadcast is already running")

        normalized_message = self._normalize_message(message)

        async with broadcast_lock:
            users = await self.user_repository.get_all_users(self.db)
            result = await self._broadcast_users(users, normalized_message)
            logger.info(
                "Broadcast finished for all users | attempted={attempted} sent={sent} "
                "failed_temporary={failed_temporary} "
                "failed_permanent={failed_permanent} skipped_invalid={skipped_invalid}",
                attempted=result.attempted,
                sent=result.sent,
                failed_temporary=result.failed_temporary,
                failed_permanent=result.failed_permanent,
                skipped_invalid=result.skipped_invalid_user,
            )
            return result

    async def broadcast_for_users_with_role(self, role_name: str, message: str) -> BroadcastResult:
        broadcast_lock = self._get_broadcast_lock()
        if broadcast_lock.locked():
            raise BroadcastAlreadyRunningError("Broadcast is already running")

        normalized_role_name = self._normalize_role(role_name)
        normalized_message = self._normalize_message(message)

        async with broadcast_lock:
            users = await self.user_repository.get_all_users_with_role(self.db, normalized_role_name)
            result = await self._broadcast_users(users, normalized_message)
            logger.info(
                "Broadcast finished for role={role_name} | attempted={attempted} sent={sent} "
                "failed_temporary={failed_temporary} "
                "failed_permanent={failed_permanent} skipped_invalid={skipped_invalid}",
                role_name=normalized_role_name,
                attempted=result.attempted,
                sent=result.sent,
                failed_temporary=result.failed_temporary,
                failed_permanent=result.failed_permanent,
                skipped_invalid=result.skipped_invalid_user,
            )
            return result

    async def broadcast_for_users_with_competence(self, competence_id: int, message: str) -> BroadcastResult:
        broadcast_lock = self._get_broadcast_lock()
        if broadcast_lock.locked():
            raise BroadcastAlreadyRunningError("Broadcast is already running")

        normalized_competence_id = self._normalize_competence_id(competence_id)
        normalized_message = self._normalize_message(message)

        async with broadcast_lock:
            users = await self.user_repository.get_all_users_with_competence_id(self.db, normalized_competence_id)
            result = await self._broadcast_users(users, normalized_message)
            logger.info(
                "Broadcast finished for competence_id={competence_id} | attempted={attempted} sent={sent} "
                "failed_temporary={failed_temporary} "
                "failed_permanent={failed_permanent} skipped_invalid={skipped_invalid}",
                competence_id=normalized_competence_id,
                attempted=result.attempted,
                sent=result.sent,
                failed_temporary=result.failed_temporary,
                failed_permanent=result.failed_permanent,
                skipped_invalid=result.skipped_invalid_user,
            )
            return result
