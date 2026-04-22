"""Compatibility shim for legacy imports from ``pybot.health.app``.

This module keeps backward-compatible imports while delegating app assembly to
``pybot.health.main`` as the single source of truth.
"""

from __future__ import annotations

from .main import app, create_app
from .routers.health import health
from .routers.readiness import ready

__all__ = ["app", "create_app", "health", "ready"]
