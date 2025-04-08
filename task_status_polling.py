import asyncio
import aiohttp
from typing import Optional
from endpoints import status_polling_endpoint
from utils import eprint


class TaskStatusPolling:
    def __init__(self, task_id, interval_seconds: int = 300):
        self.interval = interval_seconds
        self.__task_id = task_id
        self._task: Optional[asyncio.Task] = None
        self._session: Optional[aiohttp.ClientSession] = None
        self._stopped = asyncio.Event()

    async def _poll_loop(self):
        self._session = aiohttp.ClientSession()
        try:
            while not self._stopped.is_set():
                await self.check_status()
                await asyncio.wait(
                    [self._stopped.wait()],
                    timeout=self.interval
                )
        finally:
            await self._session.close()

    async def check_status(self):
        try:
            async with self._session.get(status_polling_endpoint(self.__task_id)) as resp:
                data = await resp.json()
                print(f"[{resp.status}] Response: {data}")
        except Exception as e:
            eprint(f"Error checking status: {e}")

    def start(self):
        if self._task is None or self._task.done():
            self._stopped.clear()
            self._task = asyncio.create_task(self._poll_loop())

    async def stop(self):
        self._stopped.set()
        if self._task:
            await self._task
