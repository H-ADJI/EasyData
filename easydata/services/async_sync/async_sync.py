'''
Filename: async_sync.py
Created Date: 
Author: 

Copyright (c) 2021 Henceforth
'''
import asyncio
from typing import Coroutine, Awaitable
from threading import Thread, Event
from concurrent import futures


class AioThread(Thread):
    """Running Async code in sync way
    """

    def __init__(self, *args, **kwargs):
        """Startting the loop and launching the event
        """
        super().__init__(*args, **kwargs)
        self.loop, self.event = None, Event()

    def run(self):
        """Run the loop
        """
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)
        self.loop.call_soon(self.event.set)
        self.loop.run_forever()

    def add_task(self, coro: Coroutine or Awaitable):
        """Run a task
        """
        # if the passed instance is not a  Coroutine
        if not asyncio.iscoroutine(coro):
            # wrapp it in a coroutine
            coro = self.wrapper(coro)
        # return future object
        return asyncio.run_coroutine_threadsafe(coro, loop=self.loop)

    def finalize(self):
        """Finalize the work
        """
        self.loop.call_soon_threadsafe(self.loop.stop)
        self.join()

    async def wrapper(self, awaitable: Awaitable):
        """wrapping a coroutine to an awaitable
        """
        await awaitable


def async_to_sync(aio_thread: AioThread, coroutine: Coroutine, timeout: int = None, default: object = None):
    # TODO reset timeout value, None may cause undetectable issues while debugging
    """Moving part from to async
    """
    # add future task
    future = aio_thread.add_task(coroutine)
    try:
        result = future.result(timeout)
    except futures.TimeoutError:
        print('The coroutine took too long, cancelling the task')
        future.cancel()
        return default
    except Exception as exc:
        from easydata.services.utils import logger
        print('The coroutine raised an exception: {!r}'.format(exc))
        return default
    # return the current
    return result
