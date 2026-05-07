from __future__ import annotations

from .taskiq_app import get_taskiq_broker, get_taskiq_scheduler

# Единая точка входа для `taskiq worker` и `taskiq scheduler`.
broker = get_taskiq_broker()
scheduler = get_taskiq_scheduler()
