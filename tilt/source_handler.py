from abc import ABC, abstractmethod
import aiofiles
import asyncio
from sectioner import reconstruct_file, deconstruct_file, Chunk
from sectioner import split_video as sectioner_split_video
from sectioner import reconstruct_video as sectioner_reconstruct_video


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

    async def write(self, batches: list[list[str]]):
        async with aiofiles.open(self.__filepath, 'w', encoding='utf-8') as f:
            for batch in batches:
                for line in batch:
                    await f.write(line + '\n')


class BinarySourceHandler(SourceHandler):
    def __init__(self, filepath: str, chunk_size: int = 1024, batch_size: int = 1):
        self.__filepath = filepath
        self.__chunk_size = chunk_size
        self.__batch_size = batch_size

    async def read(self):
        for chunk in deconstruct_file(self.__filepath, self.__chunk_size):
            yield chunk

    async def write(self, chunks: list[Chunk], output_file):
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


class VideoHandler(SourceHandler):
    def __init__(self, filename: str = None, output_dir: str = None, input_dir: str = None, target_filename: str = None):
        self.__filename = filename
        self.__output_dir = output_dir
        self.__input_dir = input_dir
        self.__target_filename = target_filename

    def split_video(self, filename, output_dir):
        filename = filename or self.__filename
        output_dir = output_dir or self.__output_dir
        sectioner_split_video(filename, output_dir, None)

    def reconstruct_video(self, input_dir, target_filename):
        input_dir = input_dir or self.__input_dir
        target_filename = target_filename or self.__target_filename
        sectioner_reconstruct_video(input_dir, target_filename)
