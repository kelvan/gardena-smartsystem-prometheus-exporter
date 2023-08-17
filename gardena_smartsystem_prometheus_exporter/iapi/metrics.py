from prometheus_client.metrics import Gauge

from ..config import Location
from ..log import get_logger
from .websocket import handle_websocket

logger = get_logger()


async def collect():
    metric = Gauge(
        "sg_device_attribute_value",
        "Value of device attributes",
        ["username", "device_id", "type", "attribute", *Location().extra_labels],
    )

    logger.info("Initial collect")

    await handle_websocket(metric)
