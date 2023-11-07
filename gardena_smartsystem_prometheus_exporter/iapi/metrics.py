from prometheus_client.metrics import Gauge

from ..config import Location
from ..log import get_logger
from .websocket import handle_websocket

logger = get_logger()


async def collect():
    metric = Gauge(
        "sg_device_attribute_value",
        "Value of device attributes",
        [
            "username",
            "location_id",
            "device_id",
            "type",
            "attribute",
            *Location().common_labels,
        ],
    )

    logger.info("Initial collect")

    await handle_websocket(metric)
