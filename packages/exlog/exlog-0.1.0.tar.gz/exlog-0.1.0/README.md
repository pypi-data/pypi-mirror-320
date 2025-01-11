# ExLog

![Python](https://img.shields.io/badge/python-%3E%3D3.7-blue.svg) ![License: MIT](https://img.shields.io/badge/License-MIT-brightgreen.svg)

**A lightweight, colorful, customizable Python logging utility with support for terminal output, file rotation, and asynchronous logging; built for the Ex Projects, and YOURs too!**
## Table of Contents
1. [Overview](#overview)
2. [Installation](#installation)
3. [Usage Examples](#usage-examples)
4. [Feature Demonstrations](#feature-demonstrations)
5. [Configuration](#configuration)
6. [Available Colors](#available-colors)
7. [Contributing](#contributing)
8. [License](#license)

---

## Overview
`ExLog` is a flexible logging utility that supports both console and file-based logging with:
- Customizable log levels (`debug`, `info`, `warning`, `error`, `critical`).
- Colored output for better readability.
- File rotation by **time** (`daily`, `hourly`) and **size**.
- Asynchronous logging with minimal overhead.

---

## Installation
Ensure that `termcolor` is installed for colored console output:
```bash
pip install termcolor
```
Alternatively, you can include it in your `requirements.txt`.

To clone the repository:
```bash
git clone https://github.com/onedavidwilliams/ExLog.git
cd ExLog
```

---

## Minimum Python Version
`ExLog` requires **Python 3.7 or higher**. for asyncio.run() to work correctly

---
### How It Works:
- When you instantiate `ExLog`, you can set the minimum `log_level`. Only messages with a **numeric value greater than or equal** to the set level will be printed.
- You can specify the `log_level` using a **string** (e.g., `"debug"`, `"info"`, etc.) or **number** (`1`, `2`, etc.).

### Usage Examples:
### 1. **Log Level: `info` (1)**
   ```python
   logger = ExLog(log_level="info")  # Same as log_level=1
   logger.dprint("Info message", level="info")  # Printed
   logger.dprint("Debug message", level=2)  # Not printed - Same as "debug"
   ```

### 2. **Log Level: `debug` (2)**
   ```python
   logger = ExLog(log_level="debug")  # Same as log_level=2
   logger.dprint("Debug message", level="debug")  # Printed
   logger.dprint("Info message", level="info")  # Not Printed
   ```

### 3. **Log Level: `warning` (3)**
   ```python
   logger = ExLog(log_level="warning")  # Same as log_level=3
   logger.dprint("Warning message", level="warning")  # Printed
   logger.dprint("Info message", level="info")  # Not Printed
   logger.dprint("Debug message", level="debug")  # Not printed
  ```
### 4. **Basic Console Logging**
```python
from ExLog import ExLog

logger = ExLog()  # Default log level: info, console-only
logger.dprint("Hello, World!", level="info")
```
**Output:**
```
[03:15:20 PM] [INFO] Hello, World!
```

---

### 5. **Logging to File with Daily Rotation**
```python
logger = ExLog(log_dir="my_logs", rotation="daily")
logger.dprint("Logging to file and terminal.", level="debug")
```
- Logs are saved in the `my_logs/` directory.
- New files are created daily.

---

### 6. **Async Logging**
```python
import asyncio
from ExLog import ExLog

async def main():
    logger = ExLog(log_dir="my_logs", rotation="hourly")
    await logger.adprint("Async log message", level="info")

asyncio.run(main())
```
- Async-friendly logging for concurrent applications.

---

## Feature Demonstrations

### 1. **Size-Based Log File Rotation**
```python
logger = ExLog(log_dir="my_logs", max_file_size=1024 * 5)  # 5 KB max size
for i in range(100):
    logger.dprint(f"Message {i}", level="info")
```
- Automatically creates new log files when the size exceeds 5 KB.

---

### 2. **Custom Color Formatting**
```python
logger = ExLog(custom_colors={
    "info": {"color": ExLog.color.magenta},
    "warning": {"color": ExLog.color.blue, "background_color": ExLog.bg_color.yellow}
})
logger.dprint("Custom color for info.", level="info")
logger.dprint("Custom color for warning.", level="warning")
```

---

### 3. **Critical Log with Program Exit**
```python
def critical_exit_example(error=None):
    logger = ExLog()
    error = error if error else "No error specified"
    logger.dprint(f"Critical failure! Exiting program...\nError: {error}", level="critical")
    exit(1)

critical_exit_example("Test")
```
- Prints a critical log message and the error if one is passed and exits the program.

---

### 4. **Different Log Levels in Loop**
```python
log_levels = ["debug", "info", "warning", "error", "critical"]
logger = ExLog(log_dir="my_logs")

for i, level in enumerate(log_levels):
    logger.dprint(f"This is a {level.upper()} message", level=level)
```
- Cycles through all log levels to demonstrate their output.

---

## Configuration

### Initialization Parameters
| **Parameter**   | **Type** | **Default** | **Description** |
|-----------------|----------|-------------|-----------------|
| `log_level`     | `int`    | `1`         | Minimum log level to display (1 for "info", 2 for "debug", etc.). |
| `log_dir`       | `str`    | `None`      | Directory for log files. If `None`, logs only print to the console. |
| `log_file_prefix` | `str`  | "log"      | Prefix for log filenames. |
| `rotation`      | `str`    | "daily"    | Log rotation type: "daily", "hourly", or "none". |
| `max_file_size` | `int`    | `None`      | Maximum log file size (in bytes) before rotating to a new file. |
| `custom_colors` | `dict`   | `None`      | Dictionary for custom foreground and background colors. |

---

## Available Colors
You can set colors using `ExLog.color` (foreground) and `ExLog.bg_color` (background):

| **Foreground Colors (`ExLog.color`)** | **Background Colors (`ExLog.bg_color`)** |
|---------------------------------------|------------------------------------------|
| `black`                               | `on_black`                               |
| `red`                                 | `on_red`                                 |
| `green`                               | `on_green`                               |
| `yellow`                              | `on_yellow`                              |
| `blue`                                | `on_blue`                                |
| `magenta`                             | `on_magenta`                             |
| `cyan`                                | `on_cyan`                                |
| `white`                               | `on_white`                               |
| `grey`                                | `on_grey`                                |

---

## Contributing
1. Fork the repository.
2. Create a feature branch:
   ```bash
   git checkout -b my-feature-branch
   ```
3. Commit your changes:
   ```bash
   git commit -m "Added new feature"
   ```
4. Push your branch:
   ```bash
   git push origin my-feature-branch
   ```
5. Open a pull request.

---
