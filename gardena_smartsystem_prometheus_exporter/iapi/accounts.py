from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import ClassVar, Optional

from ..config import Location
from ..log import get_logger
from .auth import get_token
from .location import get_location

logger = get_logger()


@dataclass
class Account:
    username: str
    password: str
    location_id: str
    client_id: str
    api_key: str
    token: str
    expires: datetime
    refresh_token: str


class AccountStore:
    _account: ClassVar[Optional[Account]] = None

    @classmethod
    async def get(cls) -> Account:
        if cls._account is None or cls._account.expires < datetime.now():
            cls._account = await cls.populate()
        return cls._account

    @classmethod
    async def populate(cls) -> Account:
        location = Location().auth
        logger.info(f"Log in user {location.username}")
        password = location.password.get_secret_value()
        api_key = location.api_key.get_secret_value()
        token = await get_token(
            username=location.username,
            password=password,
            client_id=location.client_id,
        )
        access_token = token["access_token"]
        location_id = await get_location(access_token, api_key)
        expires = datetime.now() + timedelta(seconds=int(token["expires_in"]) - 15 * 60)
        return Account(
            username=location.username,
            password=password,
            location_id=location_id,
            client_id=location.client_id,
            api_key=api_key,
            token=access_token,
            refresh_token=token["refresh_token"],
            expires=expires,
        )
