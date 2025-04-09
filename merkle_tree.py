import hashlib
from chunk import Chunk


class MerkleTree:
    def __init__(self, chunk_size: int = 1024 * 1024):
        self.chunk_size = chunk_size
        self.chunks: list[Chunk] = []
        self.tree: list[list[str]] = []
        self.root_hash: str = ""

    def _hash(self, data: bytes) -> str:
        return hashlib.sha256(data).hexdigest()

    def split_and_build(self, file_path: str) -> list[Chunk]:
        self.chunks.clear()
        self.tree.clear()

        with open(file_path, "rb") as f:
            index = 0
            while chunk := f.read(self.chunk_size):
                chunk_hash = self._hash(chunk)
                self.chunks.append(Chunk(index=index, data=chunk, hash=chunk_hash))
                index += 1

        if not self.chunks:
            raise ValueError("File is empty or unreadable")

        leaf_hashes = [chunk.hash for chunk in self.chunks]
        self.tree.append(leaf_hashes)

        current = leaf_hashes
        while len(current) > 1:
            next_level = []
            for i in range(0, len(current), 2):
                left = current[i]
                right = current[i + 1] if i + 1 < len(current) else left
                parent_hash = self._hash((left + right).encode())
                next_level.append(parent_hash)
            self.tree.append(next_level)
            current = next_level

        self.root_hash = self.tree[-1][0]
        return self.chunks

    def reconstruct(self, chunks: list[Chunk], dest_path: str):
        ordered = sorted(chunks, key=lambda c: c.index)
        with open(dest_path, "wb") as f:
            for chunk in ordered:
                f.write(chunk.data)
