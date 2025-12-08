from __future__ import annotations
import os
import asyncio
from dataclasses import dataclass
from typing import AsyncGenerator, List
import aiofiles


@dataclass
class Chunk:
    index: int
    data: bytes
    filename: str

    # original filename
    total_chunks: int = 0

    def __post_init__(self):
        if isinstance(self.data, memoryview):
            self.data = bytes(self.data)


async def deconstruct_file(
    filepath: str, chunk_size: int = 1024 * 1024
) -> AsyncGenerator[Chunk]:
    """
    Split a file into chunks asynchronously.
    Yields Chunk(index, data, filename)
    """
    filename = os.path.basename(filepath)

    async with aiofiles.open(filepath, "rb") as f:
        index = 0
        while True:
            data = await f.read(chunk_size)
            if not data:
                break
            yield Chunk(index=index, data=data, filename=filename)
            index += 1


def reconstruct_file(chunks: List[Chunk], output_path: str) -> None:
    """
    Reconstruct a file from a list of Chunk objects (synchronous, fast).
    Chunks must be in correct order.
    """
    # Sort just in case
    chunks = sorted(chunks, key=lambda c: c.index)

    with open(output_path, "wb") as f:
        for chunk in chunks:
            f.write(chunk.data)


# === Video handling using ffmpeg ===


async def _run_ffmpeg(cmd: List[str]) -> None:
    proc = await asyncio.create_subprocess_exec(
        *cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
    )
    await proc.communicate()
    if proc.returncode != 0:
        raise RuntimeError(f"ffmpeg failed: {cmd}")


def split_video(input_path: str, output_dir: str, segment_time: int | None = 10):
    """
    Split video → chunks using ffmpeg
    Original behavior: split into ~10-second segments named part_000.mp4, part_001.mp4, ...
    """
    os.makedirs(output_dir, exist_ok=True)
    # -f segment -segment_time 10 -c copy -map 0 -reset_timestamps 1
    cmd = [
        "ffmpeg",
        "-i",
        input_path,
        "-f",
        "segment",
        "-segment_time",
        str(segment_time or 10),
        "-c",
        "copy",
        "-map",
        "0",
        "-reset_timestamps",
        "1",
        f"{output_dir}/part_%04d.mp4",
    ]
    # Run synchronously — it's fast and safe here
    import subprocess

    subprocess.run(cmd, check=True, capture_output=True)


def reconstruct_video(input_dir: str, output_path: str) -> None:
    """
    Recombine segmented .mp4 files back into one video.
    Requires a file list: concat list
    """
    parts = sorted(
        f for f in os.listdir(input_dir) if f.endswith(".mp4") and f.startswith("part_")
    )
    if not parts:
        raise ValueError("No video parts found")

    list_file = os.path.join(input_dir, "list.txt")
    with open(list_file, "w") as f:
        for part in parts:
            f.write(f"file '{os.path.join(input_dir, part)}'\n")

    cmd = [
        "ffmpeg",
        "-f",
        "concat",
        "-safe",
        "0",
        "-i",
        list_file,
        "-c",
        "copy",
        output_path,
    ]
    import subprocess

    subprocess.run(cmd, check=True, capture_output=True)
    os.remove(list_file)  # cleanup


__all__ = [
    "Chunk",
    "deconstruct_file",
    "reconstruct_file",
    "split_video",
    "reconstruct_video",
]
