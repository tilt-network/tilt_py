import asyncio
import aiohttp
from typing import AsyncGenerator
from utils import eprint


class Connection:
    def __init__(self, filepath: str, api_url: str, batch_size: int = 20, concurrency: int = 10):
        self.filepath = filepath
        self.api_url = api_url
        self.batch_size = batch_size
        self.concurrency = concurrency
        self.queue = asyncio.Queue(maxsize=concurrency * 2)

    async def read_batches(self) -> AsyncGenerator[list[str], None]:
        loop = asyncio.get_running_loop()
        if not self.is_textual(self.filepath):
            eprint("File is binary")
        with open(self.filepath, "r") as f:
            batch = []
            while True:
                line = await loop.run_in_executor(None, f.readline)
                if not line:
                    if batch:
                        yield batch
                    break
                batch.append(line.rstrip('\n'))
                if len(batch) == self.batch_size:
                    yield batch
                    batch = []

    async def worker(self, name: int, session: aiohttp.ClientSession):
        while True:
            batch = await self.queue.get()
            if batch is None:
                self.queue.task_done()
                break
            for line in batch:
                try:
                    async with session.post(self.api_url, data=line.encode('utf-8')):
                        continue
                except Exception as e:
                    eprint(f"Worker {name} error: {e}")
            self.queue.task_done()

    async def run(self):
        async with aiohttp.ClientSession() as session:
            tasks = [
                asyncio.create_task(self.worker(i, session))
                for i in range(self.concurrency)
            ]

            async for batch in self.read_batches():
                await self.queue.put(batch)

            # cleanup workers
            for _ in range(self.concurrency):
                await self.queue.put(None)

            await self.queue.join()
            for task in tasks:
                await task

    def is_textual(self, filepath: str):
        try:
            with open(filepath, 'rb') as file:
                block = file.read(8)  # read first 8 bytes
                if b'\0' in block:
                    return False
                try:
                    block.decode('utf-8')
                    return True
                except UnicodeDecodeError:
                    return False
        except Exception as e:
            eprint(f"Error reading file: {e}")
            return False
