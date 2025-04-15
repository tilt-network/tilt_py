import pytest
import asyncio
from tilt.source_handler import TextSourceHandler, BinarySourceHandler, TcpHandler
from unittest.mock import patch


@pytest.mark.asyncio
async def test_text_source_handler_reads_batches(monkeypatch, tmp_path):
    file_path = tmp_path / "test.txt"
    file_path.write_text("line1\nline2\nline3\n")

    handler = TextSourceHandler(str(file_path), batch_size=2)
    result = []
    async for batch in handler.read():
        result.append(batch)

    assert result == [["line1", "line2"], ["line3"]]


@pytest.mark.asyncio
async def test_binary_source_handler_reads_chunks():
    mock_chunks = [b'chunk1', b'chunk2']

    with patch("tilt.source_handler.deconstruct_file", return_value=mock_chunks):
        handler = BinarySourceHandler("fake.bin", chunk_size=5)
        result = []
        async for chunk in handler.read():
            result.append(chunk)

    assert result == mock_chunks


def test_binary_source_handler_reconstruct_file():
    chunks = [b'data']
    with patch("tilt.source_handler.reconstruct_file") as mock_reconstruct:
        handler = BinarySourceHandler("fake.bin")
        asyncio.run(handler.write(chunks, "output.bin"))
        mock_reconstruct.assert_called_once_with(chunks, "output.bin")


@pytest.mark.asyncio
async def test_tcp_handler_reads_batches(monkeypatch):
    async def mock_open_connection(host, port):
        class FakeReader:
            def __init__(self):
                self.lines = [b'line1\n', b'line2\n', b'']

            async def readline(self):
                return self.lines.pop(0)

        class FakeWriter:
            def close(self):
                pass

            async def wait_closed(self):
                pass

        return FakeReader(), FakeWriter()

    monkeypatch.setattr("tilt.source_handler.asyncio.open_connection", mock_open_connection)
    handler = TcpHandler("localhost", 1234, batch_size=2)
    result = []
    async for batch in handler.read():
        result.append(batch)

    assert result == [["line1", "line2"]]
