# bilicache/cli.py
import argparse
import os
import signal
import subprocess
import sys
from pathlib import Path

RUNTIME_DIR = Path.home() / ".cache" / "bilicache"
RUNTIME_DIR.mkdir(parents=True, exist_ok=True)
PID_FILE = RUNTIME_DIR / ".bilicache.pid"
LOG_FILE = RUNTIME_DIR / ".bilicache.log"


def start():
    if PID_FILE.exists():
        print("bilicache already running")
        return

    with open(LOG_FILE, "ab") as log:
        proc = subprocess.Popen(
            [sys.executable, "-m", "bilicache.app"],
            stdout=log,
            stderr=log,
            start_new_session=True,  # 关键：脱离当前终端
        )

    PID_FILE.write_text(str(proc.pid))
    print(f"bilicache started (pid {proc.pid})")


def stop():
    if not PID_FILE.exists():
        print("bilicache not running")
        return

    pid = int(PID_FILE.read_text())
    try:
        os.kill(pid, signal.SIGTERM)
        print("bilicache stopped")
    except ProcessLookupError:
        print("process not found")
    finally:
        PID_FILE.unlink(missing_ok=True)


def restart():
    stop()
    start()


def main():
    parser = argparse.ArgumentParser(prog="bilicache")
    sub = parser.add_subparsers(dest="command")

    sub.add_parser("start")
    sub.add_parser("stop")
    sub.add_parser("restart")

    args = parser.parse_args()

    if args.command == "start":
        start()
    elif args.command == "stop":
        stop()
    elif args.command == "restart":
        restart()
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
