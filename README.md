# Tilt Python Client

This is the official Python client for submitting and processing data in the [Tilt](https://tilt.technology) distributed computing platform.

## 🚀 Overview

Tilt enables distributed data processing by orchestrating multiple devices connected to a network.
This client is responsible for reading input files, batching the content, and sending it to the Tilt API asynchronously.

## 📦 Installation

```bash
pip install tilt-py
```

## 🧑‍💻 Usage

```python
import os
from uuid import UUID

from tilt import Options, Tilt
from tilt.source_handler import TextSourceHandler
from tilt.types import Some

# Load environment variables or set directly
SECRET_KEY = os.getenv("SECRET_KEY")  # or "your_secret_key"
PROGRAM_ID = UUID("c6e024e0-ad75-45ca-94b4-bbeadb4eebfa")  # Replace with your program ID
INPUT_FILE = "shipping_calculation.jsonl"  # Path to your input file

# Configure data source and options
data_src = TextSourceHandler(INPUT_FILE)
options = Options(
    data_src=Some(data_src),
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

print(" ".join(texts))
```

The client reads from the configured data source, batches the input, and sends it to the Tilt API for processing.

## ✅ Requirements

- Python 3.10+

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
