import pytest
import aiohttp
from unittest.mock import patch
from tilt.connection import Connection
from tilt.log import TiltLog


class FakeSource:
    def __init__(self, batches):
        self.batches = batches

    async def read(self):
        for batch in self.batches:
            yield batch


@pytest.mark.asyncio
async def test_connection_successful_dispatch(aiohttp_server):
    received = []

    async def handler(request):
        data = await request.json()
        received.append(data)
        return aiohttp.web.Response(status=200)

    app = aiohttp.web.Application()
    app.router.add_post("/dispatch", handler)
    server = await aiohttp_server(app)

    with patch("tilt.endpoints.dispatch_endpoint", return_value=server.make_url("/dispatch")):
        source = FakeSource([["a", "b"], ["c"]])
        conn = Connection(source, program_id="test", concurrency=2)
        await conn.run()

    for item in received:
        expected_payload = {"program_id": "abc123", "data": item}
        assert any(
            received_item.get("program_id") == expected_payload["program_id"] and
            received_item.get("data") == expected_payload["data"]
            for received_item in received
        ), f"Expected payload not found: {expected_payload}"


@pytest.mark.asyncio
async def test_connection_handles_http_errors(aiohttp_server):
    errors = []

    async def handler(request):
        return aiohttp.web.Response(status=500)

    app = aiohttp.web.Application()
    app.router.add_post("/dispatch", handler)
    server = await aiohttp_server(app)

    with patch("tilt.endpoints.dispatch_endpoint", return_value=server.make_url("/dispatch")), \
         patch.object(TiltLog, "error", side_effect=errors.append):
        source = FakeSource([["a"]])
        conn = Connection(source, program_id="fail", concurrency=1)
        await conn.run()

    assert any("Worker 0 error" in str(e) for e in errors)


@pytest.mark.asyncio
async def test_connection_handles_exceptions():
    with patch("tilt.endpoints.dispatch_endpoint", return_value="http://localhost:9999/dispatch"), \
         patch.object(TiltLog, "error") as mock_log:
        source = FakeSource([["a"]])
        conn = Connection(source, program_id="oops", concurrency=1)
        await conn.run()

    mock_log.assert_called()
    assert any("error" in str(c[0][0]) for c in mock_log.call_args_list)


@pytest.mark.asyncio
async def test_connection_empty_source():
    source = FakeSource([])
    with patch("tilt.endpoints.dispatch_endpoint", return_value="http://localhost:1234/dispatch"):
        conn = Connection(source, program_id="empty", concurrency=1)
        await conn.run()
