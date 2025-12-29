import os
from uuid import UUID

from tilt.options import Options
from tilt.source_handler import TextSourceHandler
from tilt.tilt import Tilt
from tilt.types import Environment, Some, is_some
from tilt.validator import is_valid_api_key

SECRET_KEY = os.getenv("SECRET_KEY")
if SECRET_KEY is None or not is_valid_api_key(SECRET_KEY):
    raise ValueError("SECRET_KEY is missing or invalid.")

PROGRAM_ID = UUID("c6e024e0-ad75-45ca-94b4-bbeadb4eebfa")
INPUT_FILE = "shipping_calculation.jsonl"

data_src = TextSourceHandler(INPUT_FILE)

options = Options(
    data_src=Some(data_src),
    program_id=Some(PROGRAM_ID),
    secret_key=Some(SECRET_KEY),
    environment=Environment.DEVELOPMENT,
)

tilt = Tilt(options)
results = tilt.create_and_poll()

texts = []
for _, item in results:
    if is_some(item):
        texts.append(item.value.decode())

print("\nResponse:\n")
print(" ".join(texts))
