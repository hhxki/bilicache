import threading
import time
from datetime import datetime

class Timer:
    def __init__(self, func, args=(), kwargs=None, interval=5):
        if kwargs is None:
            kwargs = {}
        self.func = func
        self.args = args
        self.kwargs = kwargs
        self.interval = interval
        self._flag = threading.Event()
        self._thread = threading.Thread(target=self._run)

    def _run(self):
        while not self._flag.is_set():
            self.func(*self.args, **self.kwargs)
            self._flag.wait(self.interval)

    def start(self):
        self._thread.start()

    def stop(self):
        self._flag.set()
        self._thread.join()

def print_time():
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print("现在时间：", now)


def main():
    timer = Timer(func=print_time, interval=5)
    timer.start()
    time.sleep(20)
    timer.stop()
    print("定时器停止")


if __name__ == "__main__":
    main()
