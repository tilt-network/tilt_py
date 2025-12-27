import os
from uuid import UUID

API_BASE_URL = os.getenv("API_BASE_URL", "https://staging.tilt.rest")


def programs_endpoint():
    return f"{API_BASE_URL}/programs"


def status_polling_endpoint(task_id: UUID):
    return f"{API_BASE_URL}/processed_data_status/{task_id}"


def download_processed_data_endpoint(
    organization_id: UUID, job_id: UUID, task_id: UUID
):
    return f"{API_BASE_URL}/processed_data/{organization_id}/{job_id}/processed/{task_id}.dat"


def sse_endpoint(program_id: UUID):
    return f"{API_BASE_URL}/sse/{program_id}"


def jobs_endpoint():
    return f"{API_BASE_URL}/jobs"


def tasks_endpoint():
    return f"{API_BASE_URL}/tasks"


def sk_signing_endpoint():
    return f"{API_BASE_URL}/sign_in/api_key"


def run_task_endpoint():
    return f"{API_BASE_URL}/tasks/run"
