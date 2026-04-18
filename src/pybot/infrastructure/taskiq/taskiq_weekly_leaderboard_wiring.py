from __future__ import annotations

from collections.abc import Awaitable, Callable
from dataclasses import dataclass
from typing import TYPE_CHECKING

from taskiq import TaskiqEvents

if TYPE_CHECKING:
    from taskiq import AsyncBroker, TaskiqState


@dataclass(slots=True)
class _WeeklyLeaderboardWiringState:
    ensure_weekly_leaderboard_schedule: Callable[[], Awaitable[None]] | None = None


_wiring_state = _WeeklyLeaderboardWiringState()


async def _on_client_startup_weekly(_state: TaskiqState) -> None:
    """Scheduler startup hook for weekly leaderboard periodic schedule ensure."""
    if _wiring_state.ensure_weekly_leaderboard_schedule is None:
        raise RuntimeError("Weekly leaderboard wiring callback is not configured.")

    await _wiring_state.ensure_weekly_leaderboard_schedule()


def register_weekly_leaderboard_wiring(
    broker: AsyncBroker,
    *,
    ensure_weekly_leaderboard_schedule: Callable[[], Awaitable[None]],
) -> None:
    """Attach weekly leaderboard lifecycle hooks to TaskIQ broker."""
    _wiring_state.ensure_weekly_leaderboard_schedule = ensure_weekly_leaderboard_schedule
    broker.add_event_handler(TaskiqEvents.CLIENT_STARTUP, _on_client_startup_weekly)
