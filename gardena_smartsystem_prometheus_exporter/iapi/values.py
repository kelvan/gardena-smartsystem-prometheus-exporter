import re
from typing import Union, cast

import aiohttp

from ..config import Location
from ..log import get_logger
from .accounts import AccountStore

logger = get_logger()
base_url = Location().auth.api_base_url
re_to_snake_case = re.compile(r"(?<!^)(?=[A-Z])")


def to_snake_case(string: str) -> str:
    return re_to_snake_case.sub("_", string).lower()


def to_camel_case(string: str) -> str:
    camel_string = "".join(x.capitalize() for x in string.lower().split("_"))
    return string[0].lower() + camel_string[1:]


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
                attr = to_snake_case(attribute)
                if attr in Location().common_labels:
                    value = cast(str, data["value"])
                    label_values[device_id][attr] = value
                    logger.info(f"Found attribute for device '{device_id}': {attr} = '{value}'")

    return label_values
