from prometheus_client.metrics import Gauge

from ..config import Location
from ..log import get_logger
from .websocket import handle_websocket

logger = get_logger()


async def collect():
    attribute_value_metric = Gauge(
        "sg_device_attribute_value",
        "Value of Gardena smartsystem device attributes",
        [
            "user_id",
            "location_id",
            "device_id",
            "type",
            "attribute",
            *Location().common_labels,
        ],
    )
    online_metric = Gauge(
        "sg_device_attribute_online",
        "Device online state of Gardena smartsystem devices",
        [
            "user_id",
            "location_id",
            "device_id",
            *Location().common_labels,
        ],
    )

    await handle_websocket(attribute_value_metric, online_metric)
