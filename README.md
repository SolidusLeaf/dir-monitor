# dir-monitor
# Directory Monitoring Tool

A lightweight Python tool for monitoring file system changes across multiple directories using threading and CLI arguments.

---
## Features

- Monitor multiple directories simultaneously
- Detect file creation, deletion, and modification
- CLI-based configuration
- Graceful shutdown via SIGINT (Ctrl+C)
- Lightweight and dependency-free

---
## Usage

```bash
python dir_monitor.py --dirs /path/one /path/two --interval 3

python dir_monitor -d /path/one /path/two -T 3

python dir_monitor --dirs /path/one /path/two

python dir_monitor -d /path/one /path/two
```
---
## Example output

```
[/home/user] [NEW] test.txt
[/home/user] [MODIFIED] config.json
[/home/user] [DELETED] old.log
```
---
## Architecture

- Thread per directory
- Periodic polling via os.listdir
- Signal-based shutdown (SIGINT)
- Shared stop_event for graceful termination

## Requirements

- Python 3.8+
- No external dependencies

## How it works

The tool continuously scans target directories at fixed intervals.

For each directory:
- snapshots current file state (name + modification time)
- compares with previous snapshot
- detects:
  - added files
  - removed files
  - modified files

Each directory runs in a separate thread.
Shutdown is controlled via SIGINT (Ctrl+C) using a shared threading event.

## Limitations

- Uses polling (not event-based FS monitoring)
- Not optimized for very large directory trees
- File rename detection is not explicitly handled
- Performance depends on scan interval and directory size
- 
## Motivation

This project was built to practice:
- multithreading in Python
- CLI design using argparse
- file system state tracking
- graceful shutdown handling in long-running scripts
