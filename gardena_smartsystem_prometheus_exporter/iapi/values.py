from typing import Union, cast

import aiohttp

from ..config import Location
from ..log import get_logger
from .accounts import AccountStore

logger = get_logger()
base_url = Location().auth.api_base_url


async def get_common_values() -> dict[str, dict[str, str]]:
    account = await AccountStore.get()
    url = f"{base_url}/locations/{account.location_id}"

    headers = {"authorization": f"Bearer {account.token}", "X-Api-Key": account.client_id}

    label_values: dict[str, dict[str, str]] = {}

    async with aiohttp.ClientSession() as session:
        r = await session.get(url, headers=headers)
        r.raise_for_status()
        values = cast(dict, await r.json())

    for service in values["included"]:
        if service.get("type") == "COMMON":
            device_id = cast(str, service["id"])
            label_values[device_id] = {}
            attributes = cast(dict[str, dict[str, Union[str, float]]], service["attributes"])
            for attribute, data in attributes.items():
                if attribute in Location().common_labels:
                    value = cast(str, data["value"])
                    label_values[device_id][attribute] = value
                    logger.info(f"Found attribute for device '{device_id}': {attribute} = '{value}'")

    return label_values
