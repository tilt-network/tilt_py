import asyncio
import aiohttp
import threading
from typing import Callable, Optional
from tilt.endpoints import status_polling_endpoint


class TaskStatusPolling:
    def __init__(self, program_id: str, interval: int = 15, callback: Optional[Callable[[str], None]] = None):
        self.__url = status_polling_endpoint(program_id)
        self.__interval = interval
        self.__callback = callback
        self.__stop_event = threading.Event()
        self.__thread = threading.Thread(target=self._run_loop, daemon=True)

    def start(self):
        if not self.__thread.is_alive():
            self.__thread.start()

    def stop(self):
        self.__stop_event.set()

    def _run_loop(self):
        asyncio.run(self._poll_loop())

    async def _poll_loop(self):
        async with aiohttp.ClientSession() as session:
            while not self.__stop_event.is_set():
                status = await self._check_status(session)
                if self.__callback:
                    self.__callback(status)
                await asyncio.sleep(self.__interval)

    async def _check_status(self, session: aiohttp.ClientSession) -> str:
        try:
            async with session.get(self.__url) as resp:
                return await resp.text()
        except Exception as e:
            return f"error: {e}"
