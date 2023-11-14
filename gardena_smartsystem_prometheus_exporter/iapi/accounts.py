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
    user_id: str
    location_id: str
    client_id: str
    client_secret: str
    token: str
    expires: datetime


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
        logger.info(f"Log in client_id {location.client_id}")
        client_secret = location.client_secret.get_secret_value()
        token = await get_token(
            client_id=location.client_id,
            client_secret=client_secret,
        )
        access_token = token["access_token"]
        user_id = token["user_id"]
        location_id = await get_location(access_token, location.client_id)
        expires = datetime.now() + timedelta(seconds=int(token["expires_in"]) - 15 * 60)
        return Account(
            user_id=user_id,
            location_id=location_id,
            client_id=location.client_id,
            client_secret=client_secret,
            token=access_token,
            expires=expires,
        )
