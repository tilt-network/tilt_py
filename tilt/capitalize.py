from tilt.options import Options
from tilt.tilt import Tilt
from tilt.source_handler import TextSourceHandler
import json

sk = "sk_cqAwGdgS96End4N64_mFRnkUGmvg0u4rcpNX7RxJ6KfjcO7yFx4uOFAT7j4hiK-dtMWSHMSuk15OnHpXOTWrxQ"
program_id = "7163b373-d2d2-49e4-a05e-0bdf75a1c4fe"
txt_file = "input.jsonl"

data_src = TextSourceHandler(txt_file)
options = Options(data_src, program_id, secret_key=sk)
tilt = Tilt(options)

response = tilt.create_and_poll()

texts = []
for (index, item) in response:
    # encontra o elemento bytes na tupla
    texts.append(json.loads(item.decode())["text"])

result = " ".join(texts)
print("#######################################")
print(f"Response: {result}")
print("#######################################")
