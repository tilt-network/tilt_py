import os

API_BASE_URL = os.getenv("API_BASE_URL", "https://staging.tilt.rest")


def programs_endpoint():
    return f'{API_BASE_URL}/programs'


def status_polling_endpoint(task_id: str):
    return f'{API_BASE_URL}/processed_data_status/{task_id}'


def download_processed_data_endpoint(program_path: str):
    return f'{API_BASE_URL}/processed_data/{program_path}'


def sse_endpoint(program_id: str):
    return f'{API_BASE_URL}/sse/{program_id}'


def jobs_endpoint():
    return f'{API_BASE_URL}/jobs'


def tasks_endpoint():
    return f'{API_BASE_URL}/tasks'


def sk_signing_endpoint():
    return f'{API_BASE_URL}/sign_in/api_key'


def run_task_endpoint():
    return f'{API_BASE_URL}/tasks/run'
