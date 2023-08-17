import os
from pathlib import Path
from typing import Literal, cast
from uuid import UUID

from confz import BaseConfig, EnvSource, FileSource
from pydantic import Field, HttpUrl, SecretStr

LOGLEVEL = Literal["CRITICAL", "FATAL", "ERROR", "WARNING", "WARN", "INFO", "DEBUG", "NOTSET"]


class Log(BaseConfig):  # type: ignore[misc]
    log_level: LOGLEVEL = "INFO"
    log_format: str = "[%(levelname)s] [%(asctime)s]: %(message)s"

    CONFIG_SOURCES = EnvSource(prefix="SGPE_", allow_all=True)


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
    extra_labels: list[str] = Field(default_factory=list)

    CONFIG_SOURCES = FileSource(file=os.environ.get("SGPE_CONFIG_FILE", Path(__file__).parents[1] / "config.yaml"))
