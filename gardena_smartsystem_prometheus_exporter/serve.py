import asyncio

from prometheus_client import make_asgi_app

from .metrics import collect

app = make_asgi_app(disable_compression=True)

loop = asyncio.get_event_loop()
loop.create_task(collect())
