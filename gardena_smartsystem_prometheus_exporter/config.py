import os
from pathlib import Path
from typing import ClassVar, Literal, Optional, cast

from confz import BaseConfig, EnvSource, FileSource
from pydantic import HttpUrl, SecretStr

LOGLEVEL = Literal["CRITICAL", "FATAL", "ERROR", "WARNING", "WARN", "INFO", "DEBUG", "NOTSET"]


class LogFile(BaseConfig):  # type: ignore[misc]
    file_name: Optional[str] = None
    rotate: bool = True
    rotate_max_bytes: int = 5242880
    rotate_backup_count: int = 4


class Log(BaseConfig):  # type: ignore[misc]
    log_level: LOGLEVEL = "INFO"
    log_format: str = "[%(levelname)s] [%(asctime)s]: %(message)s"
    log_file: LogFile = LogFile()

    CONFIG_SOURCES = EnvSource(prefix="SGPE_", allow_all=True, file=".env")


class LocationAuth(BaseConfig):  # type: ignore[misc]
    api_base_url: HttpUrl = cast(HttpUrl, "https://api.smart.gardena.dev/v1")
    auth_url: HttpUrl = cast(HttpUrl, "https://api.authentication.husqvarnagroup.dev/v1/oauth2/token")
    client_id: str
    client_secret: SecretStr


class Location(BaseConfig):  # type: ignore[misc]
    auth: LocationAuth
    common_labels: ClassVar[list[str]] = ["name", "serial", "model_type"]
    metric_prefix: str = "gardena_smart"

    CONFIG_SOURCES = FileSource(file=os.environ.get("SGPE_CONFIG_FILE", Path(__file__).parents[1] / "config.yaml"))
