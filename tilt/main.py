# %% Cell 1
import time
from tilt.tilt import Tilt
from tilt.options import Options
from tilt.task_status_polling import TaskStatusPolling
from tilt.processed_data import ProcessedData
from tilt.source_handler import TextSourceHandler

# %% Cell 2
program_id = 'babacdf5-db44-4b80-aa94-49693ea408c0'
data_src = TextSourceHandler('textual.txt')
options = Options('your_api_key', data_src, program_id)
"""
Instantiate Tilt object and run it
"""
tilt = Tilt(options)
tilt.run()

"""
Poll API to check task status
"""


# %% Cell 3
def handle_status(response: str):
    print("Got status:", response)


poller = TaskStatusPolling(program_id, callback=handle_status)
poller.start()

time.sleep(2)  # Let it poll a few times
poller.stop()


# %% Cell 5
"""
Fetch processed data after process
"""
data = ProcessedData(program_id, "/tmp/output.bin")
data.download()  # Automatically writes to file

data = ProcessedData(program_id)
content = data.download()  # Returns bytes
