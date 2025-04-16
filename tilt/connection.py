import asyncio
import aiohttp
from tilt.log import TiltLog
from tilt.endpoints import dispatch_endpoint
from tilt.source_handler import SourceHandler


class Connection:
    def __init__(self, source: SourceHandler, program_id: str, concurrency: int = 10):
        """
        :param source: Any object with a `read_batches()` method that returns an iterable of batches.
        :param program_id: Program identifier to include in payload.
        :param concurrency: Number of concurrent workers.
        """
        self.__source = source
        self.__program_id = program_id
        self.__concurrency = concurrency
        self.__queue = asyncio.Queue(maxsize=concurrency * 2)

    async def worker(self, name: int, session: aiohttp.ClientSession):
        while True:
            batch = await self.__queue.get()
            try:
                if batch is None:
                    break
                for item in batch:
                    try:
                        payload = {'program_id': self.__program_id, 'data': item}
                        print(payload)
                        async with session.post(dispatch_endpoint(), json=payload) as resp:
                            if resp.status != 200:
                                TiltLog.error(f"Worker {name} got status {resp.status}")
                    except Exception as e:
                        TiltLog.error(f"Worker {name} error: {e}")
            finally:
                self.__queue.task_done()

    async def run(self):
        async with aiohttp.ClientSession() as session:
            tasks = [
                asyncio.create_task(self.worker(i, session))
                for i in range(self.__concurrency)
            ]

            async for batch in self.__source.read():
                await self.__queue.put(batch)

            for _ in range(self.__concurrency):
                await self.__queue.put(None)

            await self.__queue.join()
            for task in tasks:
                await task
