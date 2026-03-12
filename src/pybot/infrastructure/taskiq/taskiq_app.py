from __future__ import annotations

from dataclasses import dataclass

from dishka import AsyncContainer
from dishka.integrations.taskiq import setup_dishka
from taskiq import AsyncBroker, TaskiqEvents, TaskiqScheduler, TaskiqState
from taskiq_redis import ListRedisScheduleSource, RedisStreamBroker

from ...core import logger, settings
from ...di.containers import setup_taskiq_container


@dataclass(slots=True)
class _TaskiqRuntimeState:
    """Хранит process-local состояние TaskIQ интеграции."""

    broker: AsyncBroker | None = None
    scheduler: TaskiqScheduler | None = None
    schedule_source: ListRedisScheduleSource | None = None
    container: AsyncContainer | None = None


_runtime_state = _TaskiqRuntimeState()


async def _on_worker_startup(_state: TaskiqState) -> None:
    """Поднимает DI-контейнер Dishka и подключает его к воркеру TaskIQ."""
    if _runtime_state.container is not None:
        logger.warning("TaskIQ worker startup hook skipped: container already initialized")
        return
    if _runtime_state.broker is None:
        raise RuntimeError("TaskIQ broker is not initialized.")

    container = setup_taskiq_container()
    setup_dishka(container=container, broker=_runtime_state.broker)
    _runtime_state.container = container
    logger.info("TaskIQ worker Dishka integration initialized")


async def _on_worker_shutdown(_state: TaskiqState) -> None:
    """Корректно закрывает DI-контейнер Dishka при остановке воркера."""
    if _runtime_state.container is None:
        logger.warning("TaskIQ worker shutdown hook skipped: container was not initialized")
        return

    await _runtime_state.container.close()
    _runtime_state.container = None
    logger.info("TaskIQ worker Dishka integration closed")


def get_taskiq_broker() -> AsyncBroker:
    """
    Возвращает singleton брокера TaskIQ для воркера и scheduler-процесса.

    Брокер создаётся лениво: основной bot/health runtime не тянет TaskIQ,
    пока отдельные процессы worker/scheduler не запущены явно.
    """
    if _runtime_state.broker is not None:
        return _runtime_state.broker

    # Для критичных задач используем stream broker с ack-семантикой.
    broker = RedisStreamBroker(settings.redis_url)

    # Интегрируем Dishka в lifecycle TaskIQ воркера через официальную интеграцию.
    broker.add_event_handler(TaskiqEvents.WORKER_STARTUP, _on_worker_startup)
    broker.add_event_handler(TaskiqEvents.WORKER_SHUTDOWN, _on_worker_shutdown)

    _runtime_state.broker = broker
    return _runtime_state.broker


def get_taskiq_schedule_source() -> ListRedisScheduleSource:
    """Возвращает singleton schedule source для scheduler-процесса."""
    if _runtime_state.schedule_source is not None:
        return _runtime_state.schedule_source

    _runtime_state.schedule_source = ListRedisScheduleSource(settings.redis_url)
    return _runtime_state.schedule_source


def get_taskiq_scheduler() -> TaskiqScheduler:
    """Возвращает singleton TaskIQ scheduler для отложенных и periodic задач."""
    if _runtime_state.scheduler is not None:
        return _runtime_state.scheduler

    broker = get_taskiq_broker()
    source = get_taskiq_schedule_source()
    _runtime_state.scheduler = TaskiqScheduler(broker=broker, sources=[source])
    return _runtime_state.scheduler
