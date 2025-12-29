import os
from uuid import UUID

from tilt.options import Options
from tilt.tilt import Tilt
from tilt.types import Environment, Some, is_some
from tilt.validator import is_valid_api_key

SECRET_KEY = os.getenv("SECRET_KEY")
if SECRET_KEY is None or not is_valid_api_key(SECRET_KEY):
    raise ValueError("SECRET_KEY is missing or invalid.")

PROGRAM_ID = UUID("c6e024e0-ad75-45ca-94b4-bbeadb4eebfa")

options = Options(
    data=Some(
        [
            b'{"origin": {"lat": -23.5505, "lon": -46.6333}, "destination": {"lat": -22.9068, "lon": -43.1729}, "priority": 1, "requested_at": 1753401600}',
            b'{"origin": {"lat": -3.7172, "lon": -38.5433}, "destination": {"lat": -8.0476, "lon": -34.8770}, "priority": 2, "requested_at": 1753401600}',
            b'{"origin": {"lat": -15.8267, "lon": -47.9218}, "destination": {"lat": -19.9167, "lon": -43.9345}, "priority": 1, "requested_at": 1753401600}',
            b'{"origin": {"lat": -12.9714, "lon": -38.5014}, "destination": {"lat": -1.4558, "lon": -48.4902}, "priority": 3, "requested_at": 1753401600}',
            b'{"origin": {"lat": -16.6869, "lon": -49.2648}, "destination": {"lat": -10.9472, "lon": -37.0731}, "priority": 2, "requested_at": 1753401600}',
            b'{"origin": {"lat": -9.9747, "lon": -67.8249}, "destination": {"lat": -3.1190, "lon": -60.0217}, "priority": 4, "requested_at": 1753401600}',
            b'{"origin": {"lat": -30.0346, "lon": -51.2177}, "destination": {"lat": -25.4284, "lon": -49.2733}, "priority": 5, "requested_at": 1753401600}',
            b'{"origin": {"lat": -5.7945, "lon": -35.2110}, "destination": {"lat": -7.1153, "lon": -34.8610}, "priority": 1, "requested_at": 1753401600}',
            b'{"origin": {"lat": -2.5307, "lon": -44.3068}, "destination": {"lat": -8.0543, "lon": -34.8813}, "priority": 2, "requested_at": 1753401600}',
            b'{"origin": {"lat": -20.4697, "lon": -54.6201}, "destination": {"lat": -12.9777, "lon": -38.5016}, "priority": 1, "requested_at": 1753401600}',
            b'{"origin": {"lat": -7.2307, "lon": -35.8811}, "destination": {"lat": -9.6659, "lon": -35.7350}, "priority": 4, "requested_at": 1753401600}',
            b'{"origin": {"lat": -1.4558, "lon": -48.4902}, "destination": {"lat": -8.0476, "lon": -34.8770}, "priority": 3, "requested_at": 1753401600}',
            b'{"origin": {"lat": -3.7172, "lon": -38.5433}, "destination": {"lat": -7.1195, "lon": -34.8450}, "priority": 3, "requested_at": 1753401600}',
            b'{"origin": {"lat": -10.9472, "lon": -37.0731}, "destination": {"lat": -12.9822, "lon": -38.4813}, "priority": 5, "requested_at": 1753401600}',
            b'{"origin": {"lat": -22.9035, "lon": -43.2096}, "destination": {"lat": -23.5505, "lon": -46.6333}, "priority": 5, "requested_at": 1753401600}',
        ]
    ),
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
