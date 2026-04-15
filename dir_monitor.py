import os
import threading
import time
import argparse
import signal
INTERVAL = 2
threads = []
previous_state = {}
WATCH_DIRS = []
MAX_DIRS = 5 # limit number of directories to monitor for performance and resource management

stop_event = threading.Event()
def handle_SIGINT(signum, frame):
    print("\n[INFO] SIGINT received. Stopping directory monitoring...")
    stop_event.set()

def scan_directory(path):
    current_state = {}
    try:
        for filename in os.listdir(path):
            full_path = os.path.join(path, filename)

            if os.path.isfile(full_path):
                current_state[filename] = os.path.getmtime(full_path)
    except Exception as e:
        print(f"[ERROR] Cannot access {path}: {e}")

    return current_state


def detect_changes(old, new):
    old_files = set(old.keys())
    new_files = set(new.keys())

    added = new_files - old_files
    removed = old_files - new_files

    modified = {
        f for f in old_files & new_files
        if old[f] != new[f]
    }

    return added, removed, modified

def monitor_directory(path):
    previous_state = scan_directory(path)

    while not stop_event.is_set():
        time.sleep(INTERVAL)

        current_state = scan_directory(path)
        added, removed, modified = detect_changes(previous_state, current_state)

        for f in added:
            print(f"[{path}] [NEW] {f}")

        for f in removed:
            print(f"[{path}] [DELETED] {f}")

        for f in modified:
            print(f"[{path}] [MODIFIED] {f}")

        previous_state = current_state


def parse_args():
    parser = argparse.ArgumentParser(description="Directory Monitoring Tool")

    parser.add_argument(
    "-d", "--dirs",
    nargs="+",
    required=True,
    help="List of directories to monitor"
    )

    parser.add_argument(
        "--interval","-T",
        type=int,
        default=2,
        help="Scan interval in seconds (default: 2)"
    )

    return parser.parse_args()

if __name__ == "__main__":
    signal.signal(signal.SIGINT, handle_SIGINT)
    args = parse_args()

    WATCH_DIRS = args.dirs
    INTERVAL = args.interval

    if INTERVAL < 1:
        print("Interval must be at least 1 second. Using default of 2 seconds.\n")
        INTERVAL = 2
        

    if len(WATCH_DIRS) > MAX_DIRS:
            print(f"Too many directories specified. Limiting to the first {MAX_DIRS}.")
            WATCH_DIRS = WATCH_DIRS[:MAX_DIRS]


    valid_dirs = []
    for path in WATCH_DIRS:
        if os.path.isdir(path):
            valid_dirs.append(path)
        else:
            print(f"WARNING: '{path}' is not a valid directory and will be skipped.\n")
    
    if not valid_dirs:
        print("[ERROR] No valid directories to monitor.\n")
        print("Use --dirs to specify valid directories.\n")
        print("Example: python dir_monitoring_agent.py --dirs /path/to/dir1 /path/to/dir2\n")
        exit(1)
        
    print(f"Monitoring {len(valid_dirs)} directories every {INTERVAL}s...")

    for path in valid_dirs:
        t = threading.Thread(target=monitor_directory, args=(path,), daemon=True)
        t.start()
        threads.append(t)
    try:
        while not stop_event.is_set():
            time.sleep(0.5)
    except KeyboardInterrupt:
        pass

    print("[INFO] Waiting for threads to finish...")

    for t in threads:
        t.join()

    print("[INFO] Shutdown complete.")
