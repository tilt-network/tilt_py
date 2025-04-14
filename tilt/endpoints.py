API_BASE_URL = "http://localhost:3000"


def dispatch_endpoint():
    return f'{API_BASE_URL}/dispatch'


def status_polling_endpoint(program_id: str):
    return f'{API_BASE_URL}/processed_data_status/{program_id}'


def download_processed_data_endpoint(program_id: str):
    return f'{API_BASE_URL}/processed_data/{program_id}'


def sse_endpoint(program_id: str):
    return f'{API_BASE_URL}/sse/{program_id}'
