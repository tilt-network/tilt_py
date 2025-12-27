# Tilt Python Client

This is the official Python client for submitting and processing data in the [Tilt](https://tilt.network) distributed computing platform.

## 🚀 Overview

Tilt enables distributed data processing by orchestrating multiple devices connected to a network.
This client is responsible for reading input files, batching the content, and sending it to the Tilt API asynchronously.

## 📁 Project Structure

```
.
├── README.md
├── pyproject.toml
├── requirements.txt
└── tilt/
    ├── __init__.py
    ├── async_executor.py
    ├── connection.py
    ├── console.py
    ├── endpoints.py
    ├── entities/
    │   ├── __init__.py
    │   ├── auth.py
    │   ├── job.py
    │   ├── organization.py
    │   ├── task.py
    │   └── user.py
    ├── log.py
    ├── main.py
    ├── options.py
    ├── processed_data.py
    ├── source_handler.py
    ├── tilt.py
    ├── types.py
    └── utils.py
```

- `tilt.py`: Main interface class (`Tilt`) used to run jobs.
- `connection.py`: Handles HTTP connections and API interactions.
- `options.py`: Manages client configuration and validation.
- `source_handler.py`: Defines handlers for different data sources (e.g., text files).
- `entities/`: Contains data models for API responses (e.g., Job, Task, User).
- `main.py`: Example script demonstrating usage.
- `utils.py`: Utility functions, including Jupyter support.
- `__init__.py`: Exposes the public API (`Tilt`, `Options`, etc.).

## 📦 Installation

You can install the library directly from Git using SSH:

```bash
pip install "git+ssh://git@github.com:tilt-network/tilt_py.git"
```

⚠️ Make sure your SSH key is added to your GitHub account.

## 🧑‍💻 Usage

```python
import os
from uuid import UUID

from tilt.options import Options
from tilt.source_handler import TextSourceHandler
from tilt.tilt import Tilt
from tilt.types import Some

# Load environment variables or set directly
SECRET_KEY = os.getenv("SECRET_KEY")  # or "your_secret_key"
PROGRAM_ID = UUID("c6e024e0-ad75-45ca-94b4-bbeadb4eebfa")  # Replace with your program ID
INPUT_FILE = "shipping_calculation.jsonl"  # Path to your input file

# Configure data source and options
data_src = TextSourceHandler(INPUT_FILE)
options = Options(
    data_src=data_src,
    program_id=Some(PROGRAM_ID),
    secret_key=Some(SECRET_KEY),
)

# Create Tilt instance and run processing
tilt = Tilt(options)
results = tilt.create_and_poll()

# Process results
texts = []
for _, item in results:
    if item is not None:
        texts.append(item.value.decode())

print("\n===================\nResponse:\n")
print(" ".join(texts))
```

The client reads from the configured data source, batches the input, and sends it to the Tilt API for processing.

## ✅ Requirements

- Python 3.8+
- A file-based dataset as input (must be a valid UTF-8 text file, e.g., JSONL)
- Valid API key (can be passed via `Options` or environment variable `SECRET_KEY`)
- Internet connection for API calls

## Common Issues & Fixes

### SSL Certificate Verification Error on macOS

If you encounter the following error when running the application:

```
ssl.SSLCertVerificationError: [SSL: CERTIFICATE_VERIFY_FAILED] certificate verify failed: unable to get local issuer certificate
```

This is a common issue on macOS with Python installations (especially Python 3.10+), as the default Python does not automatically use the system's certificate store.

**Solution**

Run the official Python certificate installer (recommended):

```bash
/Applications/Python\ 3.13/Install\ Certificates.command
```

This command installs the Mozilla root certificates bundle and updates the Python trust store.

Alternatively, if the command is not available (e.g., Homebrew, pyenv, or custom installation), update the `certifi` package:

```bash
pip install --upgrade certifi
```

After running either of these, restart your terminal or Python process and try again:

```bash
python -m tilt.main
```

This should resolve the `ClientConnectorCertificateError` and allow the application to connect to `staging.tilt.rest` successfully.