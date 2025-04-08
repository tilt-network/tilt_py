API_BASE_URL = "http://localhost:3000"


def dispatch_endpoint():
    return f'{API_BASE_URL}/dispatch'


def status_polling_endpoint(task_id: str):
    return f'{API_BASE_URL}/processed_data_status/{task_id}'


def download_processed_data_endpoint(task_id: str):
    return f'{API_BASE_URL}/processed_data/{task_id}'


def sse_endpoint(task_id: str):
    return f'{API_BASE_URL}/sse/{task_id}'
