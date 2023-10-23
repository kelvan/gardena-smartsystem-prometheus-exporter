import json
from asyncio import sleep
from typing import cast

import aiohttp
import websockets

from ..config import Location
from ..log import get_logger
from .accounts import AccountStore

base_url = Location().auth.api_base_url
logger = get_logger()


async def get_websocket_uri() -> str:
    url = f"{base_url}/websocket"
    account = await AccountStore.get()

    headers = {
        "authorization": f"Bearer {account.token}",
        "X-Api-Key": account.api_key,
        "Authorization-Provider": "husqvarna",
        "Content-Type": "application/vnd.api+json",
    }
    payload = json.dumps(
        {
            "data": {
                "id": "request-12312",
                "type": "WEBSOCKET",
                "attributes": {"locationId": account.location_id},
            }
        }
    )
    logger.info("Get websocket url")

    async with aiohttp.ClientSession() as session:
        retries = 3
        for retry in range(1, retries + 1):
            try:
                r = await session.post(url, headers=headers, data=payload, raise_for_status=True)
                j = await r.json()
                return cast(str, j["data"]["attributes"]["url"])
            except aiohttp.ClientError as e:
                if retry < retries:
                    logger.warning(f"({retry}/{retries}) Error getting websocket url: {e}")
                    logger.info("Wait for 5 seconds")
                    await sleep(5)
                else:
                    raise e
    return "this should be unreachable"


def get_device_values() -> dict[str, dict[str, list[tuple[str, dict[str, str]]]]]:
    device_values: dict[str, dict[str, list[tuple[str, dict[str, str]]]]] = {}
    for location in Location().device_values:
        device_id = str(location.device_id)
        device_values[device_id] = {}
        for device_value in location.values:
            if device_value.service_type not in device_values[device_id]:
                device_values[device_id][device_value.service_type] = []
            device_values[device_id][device_value.service_type].append(
                (device_value.attribute, device_value.extra_labels)
            )
    return device_values


async def handle_websocket(metric):
    device_values = get_device_values()
    location = Location()

    while True:
        websocket_uri = await get_websocket_uri()
        logger.info("Connecting to Websocket")
        async with websockets.connect(websocket_uri) as websocket:
            logger.info(f"Connected to WebSocket server at {websocket_uri}")

            try:
                while True:
                    # wait for value changes
                    data = await websocket.recv()
                    j = json.loads(data)
                    device_id = j.get("id")
                    service_type = j.get("type")

                    if device_id in device_values and service_type in device_values[device_id]:
                        values = j.get("attributes", {})
                        logger.debug(f"Available {service_type} resources for {device_id}: {list(values.keys())}")
                        for attribute, extra_label_values in device_values[device_id][service_type]:
                            value = values.get(attribute, {}).get("value")
                            if value is not None:
                                try:
                                    value = float(value)
                                    logger.info(f"{device_id}/{service_type}/{attribute} -> {value}")
                                    extra_labels = {
                                        label: extra_label_values.get(label, "") for label in location.extra_labels
                                    }
                                    metric.labels(
                                        username=location.auth.username,
                                        device_id=device_id,
                                        type=service_type,
                                        attribute=attribute,
                                        **extra_labels,
                                    ).set(value)
                                except ValueError as e:
                                    logger.error(f"{attribute}: {e}")
                            else:
                                logger.warning(f"Missing value for {device_id}/{service_type}/{attribute}")

            except websockets.ConnectionClosed:
                logger.info("WebSocket connection closed")
                await sleep(5)
