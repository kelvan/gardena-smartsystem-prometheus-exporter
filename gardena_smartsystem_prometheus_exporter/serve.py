import asyncio

from prometheus_client import make_asgi_app

from .metrics import collect

_prometheus_app = make_asgi_app(disable_compression=True)


async def app(scope, receive, send):
    if scope["type"] == "lifespan":
        task = None
        while True:
            message = await receive()
            if message["type"] == "lifespan.startup":
                task = asyncio.create_task(collect())
                await send({"type": "lifespan.startup.complete"})
            elif message["type"] == "lifespan.shutdown":
                if task is not None:
                    task.cancel()
                await send({"type": "lifespan.shutdown.complete"})
                return
    else:
        await _prometheus_app(scope, receive, send)
