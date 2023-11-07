import json
from asyncio import sleep
from typing import Optional, cast

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
    raise BaseException("this should be unreachable")


async def handle_websocket(metric) -> None:
    # device_values = get_device_values()
    location = Location()
    location_id = None
    label_values: dict[str, Optional[dict[str, str]]] = {}
    service_types: dict[str, list[str]] = {}

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

                    if service_type == "LOCATION":
                        location_id = device_id
                    elif service_type == "DEVICE":
                        service_types[device_id] = [
                            data.get("type")
                            for data in j.get("relationships", {}).get("services", {}).get("data", [])
                            if data.get("type")
                        ]
                    elif service_type in service_types.get(device_id, []):
                        values = j.get("attributes", {})
                        logger.debug(f"Available {service_type} resources for {device_id}: {list(values.keys())}")

                        if service_type == "COMMON":
                            new_labels = {
                                label: values.get(label, {}).get("value") for label in location.common_labels
                            }
                            if label_values.get(device_id) != new_labels:
                                if label_values.get(device_id):
                                    # this should only be happening if a device gets renamed
                                    # clear metric and reconnect to websocket

                                    logger.info(f"Common {device_id} attributes changed from {label_values[device_id]} to {new_labels}")
                                    label_values[device_id] = new_labels
                                    logger.info("Clearing metric")
                                    metric.clear()
                                    logger.info("Closing websocket")
                                    await websocket.close()
                                else:
                                    label_values[device_id] = new_labels

                        for attribute, data in values.items():
                            if device_id not in label_values:
                                logger.warning(f"No labels discovered yet for device: {device_id}")
                                continue

                            value = data.get("value")
                            if isinstance(value, (int, float)):
                                try:
                                    value = float(value)
                                    logger.info(f"{device_id}/{service_type}/{attribute} -> {value}")
                                    metric.labels(
                                        username=location.auth.username,
                                        location_id=location_id,
                                        device_id=device_id,
                                        type=service_type,
                                        attribute=attribute,
                                        **label_values[device_id],
                                    ).set(value)
                                except ValueError as e:
                                    logger.error(f"{attribute}: {e}")
                            elif value is None:
                                logger.warning(f"Missing value for {device_id}/{service_type}/{attribute} -> {value}")

            except websockets.ConnectionClosed:
                logger.info("WebSocket connection closed")
                await sleep(5)
