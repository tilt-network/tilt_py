import os
import warnings
from uuid import UUID

from dotenv import load_dotenv

from tilt.options import Options
from tilt.source_handler import TextSourceHandler
from tilt.tilt import Tilt
from tilt.types import Some, is_some


def _is_jupyter():
    try:
        from IPython.core.getipython import get_ipython

        ipy = get_ipython()
        return ipy is not None and "IPKernelApp" in ipy.config
    except (ImportError, NameError, AttributeError):
        return False


if _is_jupyter():
    try:
        import nest_asyncio

        nest_asyncio.apply()
    except ImportError:
        pass

warnings.filterwarnings(
    "ignore",
    message='install "ipywidgets" for Jupyter support',
    category=UserWarning,
    module="rich.live",
)

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")
assert SECRET_KEY is not None, "SECRET_KEY environment variable is missing"

PROGRAM_ID = UUID("c6e024e0-ad75-45ca-94b4-bbeadb4eebfa")
INPUT_FILE = "shipping_calculation.jsonl"

data_src = TextSourceHandler(INPUT_FILE)
options = Options(
    data_src=data_src,
    program_id=Some(PROGRAM_ID),
    secret_key=Some(SECRET_KEY),
)

tilt = Tilt(options)
results = tilt.create_and_poll()

texts = []
for _, item in results:
    if is_some(item):
        texts.append(item.value.decode())

print("\n===================\nResponse:\n")
print(" ".join(texts))
