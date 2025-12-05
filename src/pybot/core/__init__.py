from .config import settings
from .logger import setup_logger
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    # Этот импорт будет виден Mypy, но проигнорируется Python
    from loguru import Logger

logger: "Logger" = setup_logger()

__all__ = ["settings", "logger"]
