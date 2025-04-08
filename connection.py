import json
import asyncio
import aiohttp
from typing import AsyncGenerator
from utils import eprint

API_DISPATCH_URL = "http://localhost:3000/dispatch"


class Connection:
    def __init__(self, filepath: str, program_id: str, batch_size: int = 20, concurrency: int = 10):
        self.__filepath = filepath
        self.__program_id = program_id
        self.__batch_size = batch_size
        self.__concurrency = concurrency
        self.__queue = asyncio.Queue(maxsize=concurrency * 2)

    async def read_batches(self) -> AsyncGenerator[list[str], None]:
        loop = asyncio.get_running_loop()
        if not self.is_textual(self.__filepath):
            eprint("File is binary")
        with open(self.__filepath, "r") as f:
            batch = []
            while True:
                line = await loop.run_in_executor(None, f.readline)
                if not line:
                    if batch:
                        yield batch
                    break
                batch.append(line.rstrip('\n'))
                if len(batch) == self.__batch_size:
                    yield batch
                    batch = []

    async def worker(self, name: int, session: aiohttp.ClientSession):
        while True:
            batch = await self.__queue.get()
            if batch is None:
                self.__queue.task_done()
                break
            for line in batch:
                try:
                    json_line = json.loads(line)
                    payload = {'program_id': self.__program_id, 'data': json_line}
                    async with session.post(API_DISPATCH_URL, json=payload):
                        continue
                except Exception as e:
                    eprint(f"Worker {name} error: {e}")
            self.__queue.task_done()

    async def run(self):
        async with aiohttp.ClientSession() as session:
            tasks = [
                asyncio.create_task(self.worker(i, session))
                for i in range(self.__concurrency)
            ]

            async for batch in self.read_batches():
                await self.__queue.put(batch)

            # cleanup workers
            for _ in range(self.__concurrency):
                await self.__queue.put(None)

            await self.__queue.join()
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
