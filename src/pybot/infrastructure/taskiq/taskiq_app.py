from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from dishka import AsyncContainer
from dishka.integrations.taskiq import setup_dishka
from taskiq import AsyncBroker, AsyncTaskiqDecoratedTask, TaskiqEvents, TaskiqScheduler, TaskiqState
from taskiq.kicker import AsyncKicker
from taskiq.middlewares.smart_retry_middleware import SmartRetryMiddleware
from taskiq_redis import ListRedisScheduleSource, RedisStreamBroker

from ...core import logger
from ...core.config import BotSettings, get_settings
from ...di.containers import setup_taskiq_container
from ...dto import NotificationTaskPayload
from ...services.ports import NotificationTemporaryError
from .taskiq_weekly_leaderboard_schedule import (
    LEADERBOARD_WEEKLY_SCHEDULE_ID,
    LEADERBOARD_WEEKLY_TASK_NAME,
    WeeklyLeaderboardScheduleSpec,
)
from .taskiq_weekly_leaderboard_schedule import (
    ensure_weekly_leaderboard_schedule as ensure_weekly_leaderboard_schedule_in_source,
)
from .taskiq_weekly_leaderboard_wiring import register_weekly_leaderboard_wiring
from .tasks import TaskRegistry, register_all_tasks


@dataclass(slots=True)
class _TaskiqRuntimeState:
    """Stores process-local TaskIQ runtime objects."""

    broker: AsyncBroker | None = None
    scheduler: TaskiqScheduler | None = None
    schedule_source: ListRedisScheduleSource | None = None
    container: AsyncContainer | None = None
    task_registry: TaskRegistry | None = None


_runtime_state = _TaskiqRuntimeState()


async def _on_worker_startup(_state: TaskiqState) -> None:
    """Initialize Dishka container for TaskIQ worker process."""
    if _runtime_state.container is not None:
        logger.warning("событие=инициализация_taskiq_worker status=skipped причина=container_already_initialized")
        return
    if _runtime_state.broker is None:
        raise RuntimeError("TaskIQ broker is not initialized.")

    container = setup_taskiq_container()
    setup_dishka(container=container, broker=_runtime_state.broker)
    _runtime_state.container = container
    logger.info("событие=инициализация_taskiq_worker status=success")


async def _on_worker_shutdown(_state: TaskiqState) -> None:
    """Close Dishka container on worker shutdown."""
    if _runtime_state.container is None:
        logger.warning("событие=завершение_taskiq_worker status=skipped причина=container_not_initialized")
        return

    await _runtime_state.container.close()
    _runtime_state.container = None
    logger.info("событие=завершение_taskiq_worker status=success")


def get_taskiq_task_registry(settings: BotSettings | None = None) -> TaskRegistry:
    """Возвращает реестр зарегистрированных задач TaskIQ.

    Если брокер еще не инициализирован, выполняет его инициализацию.

    Args:
        settings: Настройки бота. Если не указаны, используются настройки по умолчанию.

    Returns:
        TaskRegistry: Реестр задач.

    Raises:
        RuntimeError: Если задачи не были зарегистрированы.
    """
    get_taskiq_broker(settings)
    if _runtime_state.task_registry is None:
        raise RuntimeError("TaskIQ tasks are not registered.")
    return _runtime_state.task_registry


def get_taskiq_notification_task(
    settings: BotSettings | None = None,
) -> AsyncTaskiqDecoratedTask[..., NotificationTaskPayload]:
    """Возвращает декорированный объект задачи для отправки уведомлений.

    Args:
        settings: Настройки бота.

    Returns:
        AsyncTaskiqDecoratedTask: Объект задачи TaskIQ.
    """
    return get_taskiq_task_registry(settings).notification_task


def get_taskiq_weekly_leaderboard_task(
    settings: BotSettings | None = None,
) -> AsyncTaskiqDecoratedTask[..., dict[str, int]]:
    """Возвращает декорированный объект задачи для публикации еженедельного лидерборда.

    Args:
        settings: Настройки бота.

    Returns:
        AsyncTaskiqDecoratedTask: Объект задачи TaskIQ.
    """
    return get_taskiq_task_registry(settings).weekly_leaderboard_task


def _resolve_publish_weekly_leaderboard_kicker() -> AsyncKicker[Any, Any]:
    return get_taskiq_weekly_leaderboard_task().kicker()


async def ensure_weekly_leaderboard_schedule(
    *,
    broker: AsyncBroker | None = None,
    schedule_source: ListRedisScheduleSource | None = None,
    settings: BotSettings | None = None,
) -> None:
    """Идемпотентно гарантирует наличие расписания еженедельного лидерборда.

    Проверяет, является ли текущий процесс планировщиком и включена ли функция в настройках.

    Args:
        broker: Брокер TaskIQ.
        schedule_source: Источник расписаний Redis.
        settings: Настройки бота.

    Raises:
        RuntimeError: Если не установлен ID получателя при включенном расписании.
    """
    runtime_settings = settings or get_settings()
    runtime_broker = broker or get_taskiq_broker(runtime_settings)
    if not runtime_broker.is_scheduler_process:
        logger.debug("событие=leaderboard_weekly_ensure status=skipped причина=not_scheduler_process")
        return

    if not runtime_settings.leaderboard_weekly_enabled:
        logger.info("событие=leaderboard_weekly_ensure status=skipped причина=disabled")
        return

    recipient_id = runtime_settings.leaderboard_weekly_recipient_id
    if recipient_id is None:
        raise RuntimeError("LEADERBOARD_WEEKLY_RECIPIENT_ID must be set when LEADERBOARD_WEEKLY_ENABLED=true")

    source = schedule_source or get_taskiq_schedule_source(runtime_settings)
    await ensure_weekly_leaderboard_schedule_in_source(
        source=source,
        spec=WeeklyLeaderboardScheduleSpec(
            recipient_id=recipient_id,
            cron_expression=str(runtime_settings.leaderboard_weekly_cron),
            timezone_name=str(runtime_settings.leaderboard_weekly_timezone),
            limit=runtime_settings.leaderboard_weekly_limit,
            message_thread_id=runtime_settings.leaderboard_weekly_thread_id,
            schedule_id=LEADERBOARD_WEEKLY_SCHEDULE_ID,
            task_name=LEADERBOARD_WEEKLY_TASK_NAME,
        ),
        resolve_kicker=_resolve_publish_weekly_leaderboard_kicker,
    )


def get_taskiq_broker(settings: BotSettings | None = None) -> AsyncBroker:
    """Возвращает синглтон брокера TaskIQ.

    Args:
        settings: Настройки бота.

    Returns:
        AsyncBroker: Объект брокера TaskIQ.
    """
    if _runtime_state.broker is not None:
        return _runtime_state.broker

    runtime_settings = settings or get_settings()
    broker = RedisStreamBroker(runtime_settings.redis_url)
    _runtime_state.task_registry = register_all_tasks(
        broker=broker,
        settings=runtime_settings,
    )
    broker.add_event_handler(TaskiqEvents.WORKER_STARTUP, _on_worker_startup)
    broker.add_event_handler(TaskiqEvents.WORKER_SHUTDOWN, _on_worker_shutdown)
    register_weekly_leaderboard_wiring(
        broker,
        ensure_weekly_leaderboard_schedule=ensure_weekly_leaderboard_schedule,
    )
    broker.add_middlewares(
        SmartRetryMiddleware(
            default_retry_count=runtime_settings.leaderboard_weekly_retry_max_retries,
            default_retry_label=False,
            default_delay=float(runtime_settings.leaderboard_weekly_retry_delay_s),
            use_jitter=runtime_settings.leaderboard_weekly_retry_use_jitter,
            use_delay_exponent=runtime_settings.leaderboard_weekly_retry_use_exponential_backoff,
            max_delay_exponent=float(runtime_settings.leaderboard_weekly_retry_max_delay_s),
            schedule_source=get_taskiq_schedule_source(runtime_settings),
            types_of_exceptions=(NotificationTemporaryError,),
        )
    )

    _runtime_state.broker = broker
    return _runtime_state.broker


def get_taskiq_schedule_source(settings: BotSettings | None = None) -> ListRedisScheduleSource:
    """Возвращает синглтон источника расписаний для планировщика.

    Args:
        settings: Настройки бота.

    Returns:
        ListRedisScheduleSource: Объект источника расписаний.
    """
    if _runtime_state.schedule_source is not None:
        return _runtime_state.schedule_source

    runtime_settings = settings or get_settings()
    _runtime_state.schedule_source = ListRedisScheduleSource(runtime_settings.redis_url)
    return _runtime_state.schedule_source


def get_taskiq_scheduler(settings: BotSettings | None = None) -> TaskiqScheduler:
    """Возвращает синглтон планировщика TaskIQ.

    Args:
        settings: Настройки бота.

    Returns:
        TaskiqScheduler: Объект планировщика.
    """
    if _runtime_state.scheduler is not None:
        return _runtime_state.scheduler

    runtime_settings = settings or get_settings()
    broker = get_taskiq_broker(runtime_settings)
    source = get_taskiq_schedule_source(runtime_settings)
    _runtime_state.scheduler = TaskiqScheduler(broker=broker, sources=[source])
    return _runtime_state.scheduler
