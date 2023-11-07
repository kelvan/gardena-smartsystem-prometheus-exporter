import os
from collections.abc import Iterable
from pathlib import Path
from typing import Literal, Optional, cast
from uuid import UUID

from confz import BaseConfig, EnvSource, FileSource
from pydantic import Field, HttpUrl, SecretStr

LOGLEVEL = Literal["CRITICAL", "FATAL", "ERROR", "WARNING", "WARN", "INFO", "DEBUG", "NOTSET"]


class LogFile(BaseConfig):  # type: ignore[misc]
    file_name: Optional[str] = None
    rotate: bool = True
    rotate_max_bytes: int = 5242880
    rotate_backup_count: int = 4


class Log(BaseConfig):  # type: ignore[misc]
    log_level: LOGLEVEL = "INFO"
    log_format: str = "[%(levelname)s] [%(asctime)s]: %(message)s"
    log_file: LogFile

    CONFIG_SOURCES = EnvSource(prefix="SGPE_", allow_all=True, file=".env")


class DeviceValue(BaseConfig):  # type: ignore[misc]
    service_type: str = Field(alias="type")
    attribute: str
    extra_labels: dict[str, str] = Field(default_factory=dict)


class DeviceValues(BaseConfig):  # type: ignore[misc]
    device_id: UUID
    values: list[DeviceValue]


class LocationAuth(BaseConfig):  # type: ignore[misc]
    api_base_url: HttpUrl = cast(HttpUrl, "https://api.smart.gardena.dev/v1")
    auth_url: HttpUrl = cast(HttpUrl, "https://iam-api.dss.husqvarnagroup.net/api/v3/oauth2/token")
    username: str
    password: SecretStr
    client_id: str
    api_key: SecretStr


class Location(BaseConfig):  # type: ignore[misc]
    auth: LocationAuth
    device_values: list[DeviceValues]

    @property
    def extra_labels(self) -> Iterable[str]:
        labels: set[str] = set()

        for device_value in Location().device_values:
            for value in device_value.values:
                labels.update(value.extra_labels.keys())
        return labels

    CONFIG_SOURCES = FileSource(file=os.environ.get("SGPE_CONFIG_FILE", Path(__file__).parents[1] / "config.yaml"))
