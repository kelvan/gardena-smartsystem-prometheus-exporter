from typing import cast

import aiohttp

from ..config import Location
from ..log import get_logger

url = str(Location().auth.auth_url)
logger = get_logger()


async def get_token(username: str, password: str, client_id: str) -> dict:
    params = {
        "grant_type": "password",
        "username": username,
        "password": password,
        "client_id": client_id,
    }
    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        "Accept": "application/json",
        "Cache-Control": "no-cache",
    }
    logger.info(f"Get token for user: {username}")

    async with aiohttp.ClientSession() as session:
        r = await session.post(url, headers=headers, data=params)
        r.raise_for_status()

        return cast(dict, await r.json())
