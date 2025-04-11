from abc import ABC, abstractmethod
import aiofiles
import asyncio
from sectioner import reconstruct_file, deconstruct_file


class SourceHandler(ABC):

    def __init__(self, filepath):
        self.__filepath = filepath

    @abstractmethod
    def read(self):
        pass


class TextSourceHandler(SourceHandler):
    def __init__(self, filepath: str, batch_size: int = 1):
        self.__filepath = filepath
        self.__batch_size = batch_size

    async def read(self):
        async with aiofiles.open(self.__filepath, 'r', encoding='utf-8') as f:
            batch = []
            async for line in f:
                batch.append(line.rstrip('\n'))
                if len(batch) == self.__batch_size:
                    yield batch
                    batch = []
            if batch:
                yield batch


class BinarySourceHandler(SourceHandler):
    def __init__(self, filepath: str, chunk_size: int = 1024, batch_size: int = 1):
        self.__filepath = filepath
        self.__chunk_size = chunk_size
        self.__batch_size = batch_size

    async def read(self):
        for chunk in deconstruct_file(self.__filepath, self.__chunk_size):
            yield chunk

    async def write(self, chunks, output_file):
        reconstruct_file(chunks, output_file)


class TcpHandler(SourceHandler):
    def __init__(self, host: str, port: int, batch_size: int = 1, encoding='utf-8'):
        self.__host = host
        self.__port = port
        self.__batch_size = batch_size
        self.__encoding = encoding

    async def read(self):
        reader, writer = await asyncio.open_connection(self.__host, self.__port)
        batch = []
        try:
            while True:
                line = await reader.readline()
                if not line:
                    break
                batch.append(line.decode(self.__encoding).rstrip('\n'))
                if len(batch) == self.__batch_size:
                    yield batch
                    batch = []
            if batch:
                yield batch
        finally:
            writer.close()
            await writer.wait_closed()
