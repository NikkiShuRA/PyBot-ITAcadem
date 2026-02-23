from __future__ import annotations

from datetime import datetime
from typing import Literal

from .base_dto import BaseDTO


class HealthCheckDTO(BaseDTO):
    name: str
    status: Literal["ok", "fail"]
    details: str | None = None
    latency_ms: int | None = None


class HealthStatusDTO(BaseDTO):
    status: Literal["ok", "fail"]
    checks: list[HealthCheckDTO]
    timestamp: datetime
