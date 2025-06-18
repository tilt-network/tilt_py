import json
from tilt.options import Options
from tilt.tilt import Tilt
from tilt.source_handler import TextSourceHandler

# ——— Tilt setup ———
SECRET_KEY = "sk_cqAwGdgS96End4N64_mFRnkUGmvg0u4rcpNX7RxJ6KfjcO7yFx4uOFAT7j4hiK-dtMWSHMSuk15OnHpXOTWrxQ"
PROGRAM_ID = "d826215d-2e26-4978-96c7-f67de4262f72"
INPUT_FILE = "linear_regression.jsonl"

# initialize Tilt
data_src = TextSourceHandler(INPUT_FILE)
options  = Options(data_src, PROGRAM_ID, secret_key=SECRET_KEY)
tilt     = Tilt(options)

# send batches and wait for all segment updates
response = tilt.create_and_poll()

# parse each segment’s JSON into a dict
# updates = [
#     json.loads(raw.decode("utf-8"))
#     for _, raw in response
# ]
updates = [
    json.loads(raw.decode("utf-8"))
    for _, raw in response
    if raw is not None
]

# aggregate: simple average over segments
d0_vals = [u["d_theta0"] for u in updates]
d1_vals = [u["d_theta1"] for u in updates]
n = len(updates)

final_d0 = sum(d0_vals) / n
final_d1 = sum(d1_vals) / n

# expected gradient from a single batch: (-2.5, -7.5)
expected_d0, expected_d1 = -2.5, -7.5

# verify
assert abs(final_d0 - expected_d0) < 1e-10, (
    f"d_theta0 expected {expected_d0}, got {final_d0}"
)
assert abs(final_d1 - expected_d1) < 1e-10, (
    f"d_theta1 expected {expected_d1}, got {final_d1}"
)

print("✅ Final aggregated gradient is correct:")
print(f"   d_theta0 = {final_d0}")
print(f"   d_theta1 = {final_d1}")
