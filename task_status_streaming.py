import aiohttp
import asyncio
from endpoints import sse_endpoint
from log import Log


class TaskStatusStreaming:
    def __init__(self, task_id: str):
        self.__task_id = task_id
        self._session: aiohttp.ClientSession | None = None
        self._task: asyncio.Task | None = None
        self._stopped = asyncio.Event()

    async def _listen(self):
        self._session = aiohttp.ClientSession()
        try:
            async with self._session.get(sse_endpoint(self.__task_id), headers={"Accept": "text/event-stream"}) as resp:
                if resp.status != 200:
                    raise Exception(f"SSE connection failed: {resp.status}")

                async for line in resp.content:
                    if self._stopped.is_set():
                        break

                    decoded = line.decode().strip()
                    if not decoded:
                        continue  # skip keep-alive or empty lines

                    if decoded.startswith("data:"):
                        data = decoded.removeprefix("data:").strip()
                        self.handle_event(data)
        except Exception as e:
            Log.error(f"SSE error: {e}")
        finally:
            await self._session.close()

    def handle_event(self, data: str):
        return data

    def start(self):
        if self._task is None or self._task.done():
            self._stopped.clear()
            self._task = asyncio.create_task(self._listen())

    async def stop(self):
        self._stopped.set()
        if self._task:
            await self._task
