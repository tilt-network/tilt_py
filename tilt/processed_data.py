import aiohttp
import asyncio
import os
from tilt.endpoints import download_processed_data_endpoint
from tilt.log import TiltLog
from tilt.source_handler import BinarySourceHandler


class ProcessedData:
    def __init__(self, program_id: str, dest_path: str = None, chunk_size: int = 1024 * 1024):
        self.__program_id = program_id
        self.__chunk_size = chunk_size
        self.__dest_path = dest_path

    def download(self):
        try:
            loop = asyncio.get_running_loop()
            return loop.create_task(self.__download_or_fetch())
        except RuntimeError:
            return asyncio.run(self.__download_or_fetch())

    async def __download_or_fetch(self):
        if self.__dest_path:
            return await self.__download_to_file()
        return await self.__fetch_bytes()

    async def __fetch_bytes(self) -> bytes:
        async with aiohttp.ClientSession() as session:
            async with session.get(download_processed_data_endpoint(self.__program_id)) as resp:
                if resp.status != 200:
                    raise Exception(f"Download failed: {resp.status}")
                data = await resp.read()
                TiltLog.success(f"Downloaded {len(data)} bytes")
                return data

    async def __download_to_file(self):
        os.makedirs(os.path.dirname(self.__dest_path), exist_ok=True)

        async with aiohttp.ClientSession() as session:
            async with session.get(download_processed_data_endpoint(self.__program_id)) as resp:
                if resp.status != 200:
                    raise Exception(f"Download failed: {resp.status}")

                chunks = []
                async for chunk in resp.content.iter_chunked(self.__chunk_size):
                    chunks.append(chunk)
                    TiltLog.success(f"Fetched {len(chunk)} bytes...")

        # Delegate to BinarySourceHandler to write
        handler = BinarySourceHandler(self.__dest_path, chunk_size=self.__chunk_size)
        await handler.write(chunks, self.__dest_path)

        TiltLog.success(f"Download complete: {self.__dest_path}")
        return self.__dest_path
