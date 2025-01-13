# Appcomm Python Logger

This package provides a custom logging solution with colorized output for the terminal and detailed logs saved to a file. It is designed to handle log messages at different severity levels (DEBUG, INFO, WARNING, ERROR, and CRITICAL) and to log exception details with tracebacks for better debugging.

## Features

- **Colorized Console Output**: Logs are colorized for easy identification based on their severity (e.g., green for INFO, red for ERROR).
- **Log File**: All log messages are saved in log file, with detailed timestamps and log levels.
- **Exception Handling**: Supports logging exception details, including full tracebacks, making it easier to diagnose issues.
- **Customizable Directory**: The directory for log files can be customized, with a default of `./logs`.

## Installation

To install the `Appcomm_python_Logger` package, you can simply copy the logger class into your project or install it via a package manager if it has been uploaded to PyPI.

```bash
pip install Appcomm_python_Logger
```

## Usage

To use the logger, you can import the `Logger` class and create an instance of it in your code. You can then log messages at different severity levels using the `debug()`, `info()`, `warning()`, `error()`, and `critical()` methods.

```python
from Appcomm_python_Logger import Logger

logger = Logger()

logger.debug("This is a debug message.")
logger.info("This is an info message.")
logger.warning("This is a warning message.")
logger.error("This is an error message.")
logger.critical("This is a critical message.")
```

## Logging with Exceptions
To log an exception with a traceback, use the exc argument:

```python
try:
    # Simulate an operation that raises an exception
    raise Exception("Failed to connect to the SFTP server")
except Exception as e:
    logger.error("An error occurred while connecting to the SFTP server", exc=e)
```

## Customizing the Log File Directory

By default, log messages are displayed in the terminal with colorized output and saved to a log file in the `./logs` directory. You can customize the log file directory by passing a `log_dir` argument to the `Logger` class.

```python
logger = Logger(log_dir="./my_logs")
```

## Author

This logger package was created by Furkan Öztürk (https://furkanozturk.nl/), intern for Appcomm (https://appcomm.nl).

