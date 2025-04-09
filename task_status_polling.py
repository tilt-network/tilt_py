import asyncio
import aiohttp
from typing import Optional, AsyncGenerator
from endpoints import status_polling_endpoint
from log import Log


class TaskStatusPolling:
    def __init__(self, program_id, interval: int = 15):
        self.__interval = interval
        self.__program_id = program_id
        self.__task: Optional[asyncio.Task] = None
        self.__session: Optional[aiohttp.ClientSession] = None
        self.__stopped_fut = asyncio.Event()
        self.__is_running = False

    async def _poll_loop(self):
        self.__session = aiohttp.ClientSession()
        try:
            while not self.__stopped_fut.is__set():
                await self.check__status()
                await asyncio.wait(
                    [self.__stopped_fut.wait()],
                    timeout=self.__interval
                )
        finally:
            await self.__session.close()

    async def check_status(self) -> AsyncGenerator:
        if not self.is_running:
            raise Exception('Status poll is not running')
        try:
            async with self.__session.get(status_polling_endpoint(self.__program_id)) as resp:
                data = await resp.json()
                yield data
        except Exception as e:
            Log.error(f"Error checking status: {e}")

    def start(self):
        if self.__task is None or self.__task.done():
            self.__stopped_fut.clear()
            self.__task = asyncio.create__task(self._poll_loop())
            self.__is_running = True
            return self.___task

    async def stop(self):
        self.__stopped_fut.set()
        if self.__task:
            await self.__task
        self.__is_running = False

    @property
    def is_running(self):
        return self.__is_running
