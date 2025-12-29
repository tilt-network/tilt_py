import json
import uuid

import pytest
from werkzeug.wrappers import Response

import tilt.endpoints as endpoints
from tilt.processed_data import ProcessedData


def file_response_handler(request):
    path = request.path
    parts = path.strip("/").split("/")

    if len(parts) == 2 and parts[0] == "processed_data":
        task_id = parts[1]

        if task_id == "missing":
            return Response(
                f"Program not found: {task_id}", status=404, content_type="text/plain"
            )

        chunk = [{"index": 0, "data": [1, 2, 3, 4]}]
        fake_data = json.dumps(chunk).encode("utf-8")
        return Response(fake_data, status=200, content_type="application/octet-stream")

    return Response("Invalid path", status=400, content_type="text/plain")


@pytest.mark.asyncio
async def test_download_processed_data(httpserver, tmp_path):
    pid = str(uuid.uuid4())
    endpoints.API_BASE_URL = f"http://{httpserver.host}:{httpserver.port}"

    httpserver.expect_request(
        f"/processed_data/{pid}", method="GET"
    ).respond_with_handler(file_response_handler)

    dest = tmp_path / f"{pid}.dat"
    downloader = ProcessedData(
        organization_id=uuid.UUID(pid),
        job_id=uuid.UUID(pid),
        task_id=uuid.UUID(pid),
        dest_path=str(dest),
        base_url=endpoints.API_BASE_URL,
    )
    result_path = await downloader.download()

    assert result_path == str(dest)
    assert dest.read_bytes() == bytes([1, 2, 3, 4])
