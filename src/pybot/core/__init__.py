from __future__ import annotations

from typing import TYPE_CHECKING, Any

from .logger import setup_logger

if TYPE_CHECKING:
    from loguru import Logger


class LoggerProxy:
    """Lazy proxy to defer logger setup until first usage."""

    def __init__(self) -> None:
        self._logger: Logger | None = None

    def _get_logger(self) -> Logger:
        if self._logger is None:
            self._logger = setup_logger()
        return self._logger

    def __getattr__(self, name: str) -> Any:
        return getattr(self._get_logger(), name)


logger = LoggerProxy()

__all__ = ["logger"]
