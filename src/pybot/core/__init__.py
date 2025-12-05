from .config import settings
from .logger import setup_logger
from loguru import Logger

logger: Logger = setup_logger()

__all__ = ["settings", "logger"]
