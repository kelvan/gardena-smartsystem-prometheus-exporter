import logging
from logging import handlers
from typing import Optional

from .config import Log


class LogStore:
    logger: Optional[logging.Logger] = None


def get_logger() -> logging.Logger:
    if LogStore.logger is None:
        log_config = Log()
        log_level = getattr(logging, log_config.log_level)
        stream_handler = logging.StreamHandler()
        stream_handler.setLevel(log_level)

        log_handlers: list[logging.Handler] = [stream_handler]
        log_file_config = log_config.log_file
        if log_file := log_file_config.file_name:
            file_handler: logging.Handler
            if log_file_config.rotate:
                file_handler = handlers.RotatingFileHandler(
                    log_file,
                    maxBytes=log_file_config.rotate_max_bytes,
                    backupCount=log_file_config.rotate_backup_count,
                )
            else:
                file_handler = handlers.WatchedFileHandler(log_file)
            file_handler.setLevel(log_level)
            log_handlers.append(file_handler)
        logging.basicConfig(level=log_level, format=log_config.log_format, handlers=log_handlers)

        LogStore.logger = logging.getLogger("gardena_smartsystem_prometheus_exporter")
    return LogStore.logger
