from __future__ import annotations

from importlib import import_module

from .taskiq_app import get_taskiq_broker, get_taskiq_scheduler

# Единая точка входа для `taskiq worker` и `taskiq scheduler`.
broker = get_taskiq_broker()
scheduler = get_taskiq_scheduler()

# Импортируем задачи, чтобы декораторы @broker.task зарегистрировали их на брокере.
import_module(f"{__package__}.tasks")
