from typing import cast

import aiohttp

from ..config import Location
from ..log import get_logger

url = str(Location().auth.auth_url)
logger = get_logger()


async def get_token(client_id: str, client_secret: str) -> dict:
    params = {
        "grant_type": "client_credentials",
        "client_id": client_id,
        "client_secret": client_secret,
    }
    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        "Accept": "application/json",
        "Cache-Control": "no-cache",
    }
    logger.info(f"Get token for client_id: {client_id}")

    async with aiohttp.ClientSession() as session:
        r = await session.post(url, headers=headers, data=params)
        r.raise_for_status()

        return cast(dict, await r.json())
