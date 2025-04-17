import pytest
import time
from tilt.task_status_polling import TaskStatusPolling
import tilt.endpoints as endpoints
from werkzeug.wrappers import Response


@pytest.fixture
def program_id():
    return "abc123"


def status_response_handler(request):
    return Response("completed", status=200, content_type="text/plain")


def error_status_response_handler(request):
    return Response("error:", status=500, content_type="text/plain")


@pytest.mark.asyncio
async def test_status_polling_calls_callback(httpserver, program_id):
    statuses = []

    def callback(status):
        statuses.append(status)

    endpoints.API_BASE_URL = f"http://{httpserver.host}:{httpserver.port}"
    httpserver.expect_request(f"/processed_data_status/{program_id}", method="GET").respond_with_handler(status_response_handler)

    poller = TaskStatusPolling(program_id=program_id, interval=1, callback=callback)
    poller.start()
    time.sleep(1.5)  # let it poll a couple of times
    poller.stop()

    assert len(statuses) >= 2
    print(statuses)
    assert all(status == "completed" for status in statuses)


@pytest.mark.asyncio
async def test_status_polling_handles_errors(httpserver, program_id):
    statuses = []

    def callback(status):
        statuses.append(status)

    endpoints.API_BASE_URL = f"http://{httpserver.host}:{httpserver.port}"
    httpserver.expect_request(f"/processed_data_status/{program_id}", method="GET").respond_with_handler(error_status_response_handler)

    poller = TaskStatusPolling(program_id=program_id, interval=1, callback=callback)
    poller.start()
    time.sleep(1.5)
    poller.stop()

    assert len(statuses) >= 2
    print(statuses)
    assert all(status.startswith("error:") for status in statuses)


def test_status_polling_multiple_starts(httpserver, program_id):
    statuses = []

    def callback(status):
        statuses.append(status)

    endpoints.API_BASE_URL = f"http://{httpserver.host}:{httpserver.port}"
    httpserver.expect_request(f"/processed_data_status/{program_id}", method="GET").respond_with_handler(status_response_handler)

    poller = TaskStatusPolling(program_id=program_id, interval=1, callback=callback)
    poller.start()
    poller.start()  # should not start a second thread
    time.sleep(1)
    poller.stop()

    assert len(statuses) >= 1


def test_polling_stop_sets_event():
    poller = TaskStatusPolling(program_id="xyz")
    poller.stop()
    assert poller._TaskStatusPolling__stop_event.is_set()


def test_polling_thread_joins_gracefully():
    poller = TaskStatusPolling(program_id="xyz", interval=1)
    poller.start()
    time.sleep(0.5)
    poller.stop()
    poller._TaskStatusPolling__thread.join(timeout=2)
    assert not poller._TaskStatusPolling__thread.is_alive()
