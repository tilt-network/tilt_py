# Tilt Python Client

This is the official Python client for submitting and processing data in the [Tilt](https://tilt.network) distributed computing platform.

## 🚀 Overview

Tilt enables distributed data processing by orchestrating multiple devices connected to a network.
This client is responsible for reading input files, batching the content, and sending it to the Tilt API asynchronously.

## 📁 Project Structure

```bash
.
├── README.md
├── init.py
├── connection.py
├── options.py
├── pyproject.toml
├── requirements.txt
├── tilt.py
└── utils.py
```

- `tilt.py`: Main interface class (`Tilt`) used to run jobs.
- `connection.py`: Handles file reading and async communication with the API.
- `options.py`: Manages client configuration and local validation logic.
- `utils.py`: Utility functions such as logging.
- `__init__.py`: Exposes the public API (`Tilt`, `Options`).

## 📦 Installation

You can install the library directly from Git using SSH:

```bash
pip install "git+ssh://git@github.com:tilt-network/tilt_py.git"
```

⚠️ Make sure your SSH key is added to your GitHub account.

🧑‍💻 Usage

```py
from tilt import Tilt, Options

program_id = '...'
data_src = TextSourceHandler('...')
"""
# Configure options
"""
options = Options(
    data_src, # takes any SourceHandler implementation
    program_id=program_id,
    secret_key='your_secret_key'
)
"""
# Create Tilt instance
"""
tilt = Tilt(options)
"""
Send batches and synchronously wait for all segment updates
"""
response = tilt.create_and_poll()  # Returns bytes
```

The client will read from the configured data source, batch the input, and send it to the configured Tilt API endpoint.

✅ Requirements

- Python 3.8+
- A file-based dataset as input (must be a valid UTF-8 text file)
- Valid API key (can be passed via Options or via TILT_API_KEY environment variable)
- SQLite database at ~/tilt/tilt.db with a programs(name TEXT, program_id TEXT) table for validation
