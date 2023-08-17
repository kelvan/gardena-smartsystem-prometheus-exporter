from typing import cast

import aiohttp

from ..config import Location

base_url = Location().auth.api_base_url


async def get_location(token: str, api_key: str) -> str:
    url = f"{base_url}/locations/"

    headers = {"authorization": f"Bearer {token}", "X-Api-Key": api_key}

    async with aiohttp.ClientSession() as session:
        r = await session.get(url, headers=headers)
        r.raise_for_status()

        j = await r.json()
        return cast(str, j["data"][0]["id"])
