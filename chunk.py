from typing import NamedTuple


class Chunk(NamedTuple):
    index: int
    data: bytes
    hash: str

