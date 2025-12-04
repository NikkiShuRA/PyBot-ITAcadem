from .config import settings
from .logger import setup_logger

logger = setup_logger()

__all__ = ["settings", "logger"]
