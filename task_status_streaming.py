import aiohttp
import asyncio
from endpoints import sse_endpoint
from log import TiltLog


class TaskStatusStreaming:
    def __init__(self, program_id: str):
        self.__program_id = program_id
        self.__session: aiohttp.ClientSession | None = None
        self.__stopped = asyncio.Event()
        self.__result: str | None = None

    async def _listen(self):
        self.__session = aiohttp.ClientSession()
        try:
            async with self.__session.get(sse_endpoint(self.__program_id), headers={"Accept": "text/event-stream"}) as resp:
                if resp.status != 200:
                    raise Exception(f"SSE connection failed: {resp.status}")

                async for line in resp.content:
                    if self.__stopped.is_set():
                        break

                    decoded = line.decode().strip()
                    if not decoded:
                        continue

                    if decoded.startswith("data:"):
                        self.__result = decoded.removeprefix("data:").strip()
                        self.__stopped.set()
                        break
        except Exception as e:
            TiltLog.error(f"SSE error: {e}")
        finally:
            await self.__session.close()

    async def _start_async(self):
        self.__stopped.clear()
        await self._listen()
        return self.__result

    def start(self):
        try:
            loop = asyncio.get_running_loop()
            task = loop.create_task(self._start_async())
            return task  # Returns a coroutine to be awaited manually
        except RuntimeError:
            # No event loop running, safe to use asyncio.run
            return asyncio.run(self._start_async())
