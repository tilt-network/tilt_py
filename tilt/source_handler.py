import asyncio
from abc import ABC, abstractmethod
from typing import Any, AsyncGenerator, Optional

import aiofiles

from tilt.sectioner import Chunk, deconstruct_file, reconstruct_file
from tilt.sectioner import reconstruct_video as sectioner_reconstruct_video
from tilt.sectioner import split_video as sectioner_split_video


class SourceHandler(ABC):
    def __init__(self, filepath: str):
        self.__filepath = filepath

    @abstractmethod
    async def read(self):
        if False:
            yield

    @abstractmethod
    def jsonl_to_bytes_list(self) -> list[bytes]:
        pass


class TextSourceHandler(SourceHandler):
    def __init__(self, filepath: str, batch_size: int = 1):
        self.__filepath = filepath
        self.__batch_size = batch_size

    def jsonl_to_bytes_list(self) -> list[bytes]:
        with open(self.__filepath, "r", encoding="utf-8") as f:
            return [line.rstrip("\n").encode("utf-8") for line in f if line.strip()]

    async def read(self) -> AsyncGenerator[list[str], None]:  # type: ignore[override]
        async with aiofiles.open(self.__filepath, "r", encoding="utf-8") as f:
            batch = []
            async for line in f:
                batch.append(line.rstrip("\n"))
                if len(batch) == self.__batch_size:
                    yield batch
                    batch = []
            if batch:
                yield batch

    async def write(self, batches: list[list[str]]):
        async with aiofiles.open(self.__filepath, "w", encoding="utf-8") as f:
            for batch in batches:
                for line in batch:
                    await f.write(line + "\n")


class BinarySourceHandler(SourceHandler):
    def __init__(self, filename: str, chunk_size: int = 1024, batch_size: int = 1):
        self.__filepath = filename
        self.__chunk_size = chunk_size
        self.__batch_size = batch_size

    async def read(self) -> AsyncGenerator[Chunk, None]:  # type: ignore[override]
        async for chunk in deconstruct_file(self.__filepath, self.__chunk_size):
            yield chunk

    async def write(self, chunks: list[Chunk], output_file):
        reconstruct_file(chunks, output_file)

    def jsonl_to_bytes_list(self) -> list[bytes]:
        raise NotImplementedError(
            "BinarySourceHandler does not support jsonl_to_bytes_list"
        )


class TcpHandler(SourceHandler):
    def __init__(self, host: str, port: int, batch_size: int = 1, encoding="utf-8"):
        self.__host = host
        self.__port = port
        self.__batch_size = batch_size
        self.__encoding = encoding

    async def read(self) -> AsyncGenerator[list[str], None]:  # type: ignore[override]
        reader, writer = await asyncio.open_connection(self.__host, self.__port)
        batch = []
        try:
            while True:
                line = await reader.readline()
                if not line:
                    break
                batch.append(line.decode(self.__encoding).rstrip("\n"))
                if len(batch) == self.__batch_size:
                    yield batch
                    batch = []
            if batch:
                yield batch
        finally:
            writer.close()
            await writer.wait_closed()

    def jsonl_to_bytes_list(self) -> list[bytes]:
        raise NotImplementedError("TcpHandler does not support jsonl_to_bytes_list")


class VideoHandler(SourceHandler):
    def __init__(
        self,
        filename: Optional[str] = None,
        output_dir: Optional[str] = None,
        input_dir: Optional[str] = None,
        target_filename: Optional[str] = None,
    ):
        self.__filename = filename
        self.__output_dir = output_dir
        self.__input_dir = input_dir
        self.__target_filename = target_filename

    async def read(self) -> AsyncGenerator[Any, None]:  # type: ignore[override]
        raise NotImplementedError("VideoHandler does not support read")

    def jsonl_to_bytes_list(self) -> list[bytes]:
        raise NotImplementedError("VideoHandler does not support jsonl_to_bytes_list")

    def split_video(
        self, filename: Optional[str] = None, output_dir: Optional[str] = None
    ):
        filename = filename or self.__filename
        output_dir = output_dir or self.__output_dir
        if filename is None or output_dir is None:
            raise ValueError("filename and output_dir must be provided")
        sectioner_split_video(filename, output_dir, None)

    def reconstruct_video(
        self, input_dir: Optional[str] = None, target_filename: Optional[str] = None
    ):
        input_dir = input_dir or self.__input_dir
        target_filename = target_filename or self.__target_filename
        if input_dir is None or target_filename is None:
            raise ValueError("input_dir and target_filename must be provided")
        sectioner_reconstruct_video(input_dir, target_filename)
