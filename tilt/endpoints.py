from uuid import UUID


def programs_endpoint(base_url):
    return f"{base_url}/programs"


def status_polling_endpoint(base_url, task_id: UUID):
    return f"{base_url}/processed_data_status/{task_id}"


def download_processed_data_endpoint(
    base_url, organization_id: UUID, job_id: UUID, task_id: UUID
):
    return (
        f"{base_url}/processed_data/{organization_id}/{job_id}/processed/{task_id}.dat"
    )


def sse_endpoint(base_url, program_id: UUID):
    return f"{base_url}/sse/{program_id}"


def jobs_endpoint(base_url):
    return f"{base_url}/jobs"


def tasks_endpoint(base_url):
    return f"{base_url}/tasks"


def sk_signing_endpoint(base_url):
    return f"{base_url}/sign_in/api_key"


def run_task_endpoint(base_url):
    return f"{base_url}/tasks/run"
