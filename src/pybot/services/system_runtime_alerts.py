from __future__ import annotations

from ..core import logger
from ..core.config import BotSettings
from ..core.constants import TaskScheduleKind
from ..dto import NotifyDTO, NotifyUserDTO
from .notification_facade import NotificationFacade
from .ports import NotificationPort
from .runtime_alert_texts import runtime_shutdown_notification, runtime_startup_notification


class SystemRuntimeAlertsService:
    """Dispatch opt-in runtime alerts for the bot lifecycle."""

    def __init__(
        self,
        notification_facade: NotificationFacade,
        notification_port: NotificationPort,
        settings: BotSettings,
    ) -> None:
        self._notification_facade = notification_facade
        self._notification_port = notification_port
        self._settings = settings

    def _runtime_alerts_chat_id(self) -> int | None:
        if not self._settings.runtime_alerts_enabled:
            return None
        return self._settings.runtime_alerts_chat_id

    async def notify_startup(self) -> None:
        chat_id = self._runtime_alerts_chat_id()
        if chat_id is None:
            logger.debug("Runtime startup alert skipped because runtime alerts are disabled")
            return

        message = runtime_startup_notification(
            bot_mode=self._settings.bot_mode,
            health_api_enabled=self._settings.health_api_enabled,
        )
        await self._notification_facade.notify_user(
            NotifyUserDTO(
                recipient_id=chat_id,
                message=message,
                kind=TaskScheduleKind.IMMEDIATE,
            )
        )

    async def notify_shutdown(self) -> None:
        chat_id = self._runtime_alerts_chat_id()
        if chat_id is None:
            logger.debug("Runtime shutdown alert skipped because runtime alerts are disabled")
            return

        message = runtime_shutdown_notification(bot_mode=self._settings.bot_mode)
        await self._notification_port.send_message(NotifyDTO(recipient_id=chat_id, message=message))
