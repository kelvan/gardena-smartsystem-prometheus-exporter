import logging
from typing import Optional

from .config import Log


class LogStore:
    logger: Optional[logging.Logger] = None


def get_logger() -> logging.Logger:
    if LogStore.logger is None:
        log_config = Log()
        log_level = getattr(logging, log_config.log_level)
        handler = logging.StreamHandler()
        handler.setLevel(log_level)
        logging.basicConfig(level=log_level, format=log_config.log_format, handlers=[handler])

        LogStore.logger = logging.getLogger("gardena_smartsystem_prometheus_exporter")
    return LogStore.logger
