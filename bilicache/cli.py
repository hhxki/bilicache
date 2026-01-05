# bilicache/cli.py
import argparse
import asyncio
import os
import signal
import subprocess
import sys
import time
from pathlib import Path

from .config.cookies_locator import get_cookies
from .config.ffmpeg_locator import init_ffmpeg
from .managers.config_manager import ConfigManager

RUNTIME_DIR = Path.home() / ".cache" / "bilicache"
RUNTIME_DIR.mkdir(parents=True, exist_ok=True)

PID_FILE = RUNTIME_DIR / ".bilicache.pid"
STOP_FILE = RUNTIME_DIR / ".bilicache.stop"
LOG_FILE = RUNTIME_DIR / ".bilicache.log"


def pid_alive(pid: int) -> bool:
    try:
        os.kill(pid, 0)
    except ProcessLookupError:
        return False
    except PermissionError:
        return True
    else:
        return True


def launcher():
    config = ConfigManager()
    restart_interval = config.get("runtime", "restart_interval")
    try:
        with open(LOG_FILE, "ab") as log:
            while True:
                if STOP_FILE.exists():
                    STOP_FILE.unlink(missing_ok=True)
                    break

                start_time = time.time()

                proc = subprocess.Popen(
                    [sys.executable, "-m", "bilicache.app"],
                    stdout=log,
                    stderr=log,
                    start_new_session=True,
                )

                PID_FILE.write_text(str(proc.pid))

                while True:
                    # stop 命令
                    if STOP_FILE.exists():
                        proc.terminate()
                        try:
                            proc.wait(timeout=30)
                        except subprocess.TimeoutExpired:
                            proc.kill()
                        return

                    # worker 自己退出
                    if proc.poll() is not None:
                        break

                    # 定时重启
                    if time.time() - start_time > restart_interval:
                        proc.terminate()
                        try:
                            proc.wait(timeout=30)
                        except subprocess.TimeoutExpired:
                            proc.kill()
                        break

                    time.sleep(5)
    finally:
        PID_FILE.unlink(missing_ok=True)
        STOP_FILE.unlink(missing_ok=True)


# =========================
# CLI 命令
# =========================
def start():
    # STOP 文件永远不应该阻止 start
    STOP_FILE.unlink(missing_ok=True)
    init_ffmpeg()
    if PID_FILE.exists():
        try:
            pid = int(PID_FILE.read_text().strip())
        except Exception:
            PID_FILE.unlink(missing_ok=True)
        else:
            if pid_alive(pid):
                print(f"bilicache already running (pid={pid})")
                return
            else:
                print("stale pid file found, cleaning up")
                PID_FILE.unlink(missing_ok=True)

    subprocess.Popen(
        [sys.executable, "-m", "bilicache.cli", "--launcher"],
        start_new_session=True,
    )

    print("bilicache started")


def stop():
    if not PID_FILE.exists():
        print("bilicache not running")
        STOP_FILE.unlink(missing_ok=True)
        return

    STOP_FILE.touch()
    print("bilicache stopping...")


async def login():
    await get_cookies()
    stop()
    start()


def main():
    parser = argparse.ArgumentParser(prog="bilicache")
    parser.add_argument("--launcher", action="store_true")

    sub = parser.add_subparsers(dest="command")
    sub.add_parser("start")
    sub.add_parser("stop")
    sub.add_parser("login")

    args = parser.parse_args()

    if args.launcher:
        launcher()
    elif args.command == "start":
        start()
    elif args.command == "stop":
        stop()
    elif args.command == "login":
        asyncio.run(login())
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
