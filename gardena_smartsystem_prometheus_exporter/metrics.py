import asyncio

from .iapi.metrics import collect as iapi_collect


async def collect():
    try:
        await iapi_collect()
    except BaseException as e:
        loop = asyncio.get_event_loop()
        # kill loop in 1s
        loop.call_later(1, loop.stop)
        raise e
