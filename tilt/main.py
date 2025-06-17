from tilt.options import Options
from tilt.tilt import Tilt
from tilt.source_handler import TextSourceHandler

sk = "sk_cqAwGdgS96End4N64_mFRnkUGmvg0u4rcpNX7RxJ6KfjcO7yFx4uOFAT7j4hiK-dtMWSHMSuk15OnHpXOTWrxQ"
program_id = "7163b373-d2d2-49e4-a05e-0bdf75a1c4fe"
txt_file = "input.txt"

data_src = TextSourceHandler(txt_file)
options = Options(data_src, program_id, secret_key=sk)
tilt = Tilt(options)
job = tilt.create_job("capitalize")
job_id = job['id']
print(f"job created: {job_id}")
task = tilt.create_task(job_id, 0)
task_id = task['id']
print(f"task created: {task_id}")
resp = tilt.run_task(task_id,"{\"text\": \"hello world\"}")
print(f"task ran: {resp}")
