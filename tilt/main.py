import json
from tilt.options import Options
from tilt.tilt import Tilt
from tilt.source_handler import TextSourceHandler
from dotenv import load_dotenv
import os

load_dotenv()
# ——— Tilt setup ———
SECRET_KEY = os.getenv("SECRET_KEY")
assert SECRET_KEY is not None, "SECRET_KEY environment variable is missing"

PROGRAM_ID = "c6e024e0-ad75-45ca-94b4-bbeadb4eebfa"  # Shipping Calculation
INPUT_FILE = "shipping_calculation.jsonl"

# initialize Tilt
data_src = TextSourceHandler(INPUT_FILE)
options = Options(data_src, program_id=PROGRAM_ID, secret_key=SECRET_KEY)
tilt = Tilt(options)

# send batches and sync wait for all segment to finish
response = tilt.create_and_poll()

texts = []
for index, item in response:
    texts.append(json.loads(item.decode())["text"])

result = " ".join(texts)
print("#######################################")
print(f"Response: {result}")
print("#######################################")
