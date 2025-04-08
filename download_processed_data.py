import aiohttp
import asyncio
import os
from endpoints import download_processed_data_endpoint


class DownloadProcessedData:
    def __init__(self, task_id: str, dest_path: str, chunk_size: int = 1024 * 1024):
        self.__task_id = task_id
        self.__dest_path = dest_path
        self.__chunk_size = chunk_size

    def download(self):
        asyncio.create_task(self.download_and_write())

    async def download_and_write(self):
        os.makedirs(os.path.dirname(self.__dest_path), exist_ok=True)

        async with aiohttp.ClientSession() as session:
            async with session.get(download_processed_data_endpoint(self.__task_id)) as resp:
                if resp.status != 200:
                    raise Exception(f"Download failed: {resp.status}")
                with open(self.__dest_path, "wb") as f:
                    async for chunk in resp.content.iter_chunked(self.__chunk_size):
                        f.write(chunk)
                        print(f"Wrote {len(chunk)} bytes...")

        print(f"Download complete: {self.__dest_path}")
