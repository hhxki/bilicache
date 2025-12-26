import threading
import time
from queue import Queue
from datetime import datetime

class Event:
    def __init__(self,type_,data=None):
        self.type_=type_
        self.data=data

class EventManager:
    def __init__(self):
        self._queue=Queue()
        self._handlers={}
        self._active=False
        self._thread=threading.Thread(target=self._run)
    def _run(self):
        while self._active:
            event=self._queue.get()
            self._process(event)
    def _process(self,event:Event):
        handlers=self._handlers.get(event.type_,[])
        for handler in handlers:
            handler(event)
    def start(self):
        self._active=True
        self._thread.start()
    def stop(self):
        self._active=False
        self._queue.put(Event("__STOP__"))
        self._thread.join()
    def send_event(self,event:Event):
        self._queue.put(event)
    def add_event_listener(self,type_,handler):
        self._handlers.setdefault(type_,[])
        if handler not in self._handlers[type_]:
            self._handlers[type_].append(handler)

CHECK="check"
def print_time(event: Event):
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{event.type_}] 现在时间：{now}")



def main():
    manager = EventManager()
    manager.add_event_listener(CHECK, print_time)

    manager.start()

    for i in range(5):
        event = Event(CHECK)
        manager.send_event(event)
        time.sleep(1)

    manager.stop()
    print("事件系统已停止")


if __name__ == "__main__":
    main()
