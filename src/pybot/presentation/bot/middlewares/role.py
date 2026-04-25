"""Role-based access middleware for bot handlers."""

from collections.abc import Awaitable, Callable, Iterable
from typing import Any

from aiogram import BaseMiddleware
from aiogram.dispatcher.flags import get_flag
from aiogram.types import Message, TelegramObject
from dishka.integrations.aiogram import CONTAINER_NAME

from ....core import logger
from ....core.config import BotSettings
from ....core.constants import RolePolicyKey
from ....services import UserService
from ....utils import has_any_role
from ...texts import ROLE_ACCESS_DENIED, ROLE_AUTH_ERROR


class RoleMiddleware(BaseMiddleware):
    """Middleware that validates direct role flags and role policies."""

    @staticmethod
    def _normalize_roles(value: object) -> set[str]:
        if value is None:
            return set()
        if isinstance(value, str):
            normalized = value.strip()
            return {normalized} if normalized else set()
        if isinstance(value, Iterable):
            return {str(item).strip() for item in value if str(item).strip()}
        normalized = str(value).strip()
        return {normalized} if normalized else set()

    @staticmethod
    def _normalize_policy_keys(value: object) -> set[RolePolicyKey]:
        if value is None:
            return set()

        if isinstance(value, str | RolePolicyKey):
            raw_values: list[object] = [value]
        elif isinstance(value, Iterable):
            raw_values = list(value)
        else:
            raw_values = [value]

        available = {item.value: item for item in RolePolicyKey}
        policy_keys: set[RolePolicyKey] = set()
        for raw in raw_values:
            key_value = raw.value if isinstance(raw, RolePolicyKey) else str(raw).strip()
            matched = available.get(key_value)
            if matched is not None:
                policy_keys.add(matched)
        return policy_keys

    @staticmethod
    def _resolve_policy_roles(config: BotSettings, policy_keys: set[RolePolicyKey]) -> set[str]:
        roles: set[str] = set()
        for policy_key in policy_keys:
            value = getattr(config, policy_key.value, None)
            if value is None:
                continue
            roles.update(RoleMiddleware._normalize_roles(value))
        return roles

    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: dict[str, Any],
    ) -> Any:
        required_roles = self._normalize_roles(get_flag(data, "role"))
        required_policy_keys = self._normalize_policy_keys(get_flag(data, "role_policy"))

        if not required_roles and not required_policy_keys:
            return await handler(event, data)

        user = data.get("event_from_user")
        if not user:
            return await handler(event, data)

        user_db_id = data.get("user_id")
        if not user_db_id:
            logger.warning("Role check failed: user not found in DB")
            if isinstance(event, Message):
                await event.answer(ROLE_AUTH_ERROR)
            return

        container = data.get(CONTAINER_NAME)
        if not container:
            logger.error("Dishka container not found in data")
            return await handler(event, data)

        async with container() as request_container:
            service: UserService = await request_container.get(UserService)
            resolved_user_roles = await service.find_all_user_roles(user_id=user_db_id)
            policy_roles: set[str] = set()
            if required_policy_keys:
                config = await request_container.get(BotSettings)
                policy_roles = self._resolve_policy_roles(config, required_policy_keys)

        user_roles = resolved_user_roles or set()
        has_required_roles = has_any_role(user_roles, required_roles) if required_roles else True
        has_required_policy_roles = has_any_role(user_roles, policy_roles) if required_policy_keys else True

        logger.info(
            "Checking role access for user {user_id}",
            user_id=user.id,
        )

        if has_required_roles and has_required_policy_roles:
            return await handler(event, data)

        logger.warning(
            "Access denied for user {user_id}. required_roles={required_roles} required_policy={required_policy}",
            user_id=user.id,
            required_roles=sorted(required_roles),
            required_policy=sorted(policy_key.value for policy_key in required_policy_keys),
        )
        if isinstance(event, Message):
            await event.answer(ROLE_ACCESS_DENIED)
        return
