import threading
import time
from queue import Queue
from datetime import datetime
class Event:
    def __init__(self,type_,data=None):
        self.type_=type_
        self.data=data
class EventManger:
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
        for handler in self._handlers.get(event.type_,[]):
            result=handler(event)
            if isinstance(result,Event):
                self.send_event(result)
            elif isinstance(result,(list,tuple)):
                for e in result:
                    if isinstance(e,Event):
                        self.send_event(e)
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

class Timer:
    def __init__(self,func,args=(),kwargs=None,interval=5):
        self.func=func
        self.args=args
        self.kwargs=kwargs or {}
        self.interval=interval
        self._flag=threading.Event()
        self._thread=threading.Thread(target=self._run)
    def _run(self):
        while not self._flag.is_set():
            self.func(*self.args,**self.kwargs)
            self._flag.wait(self.interval)
    def start(self):
        self._thread.start()
        
    def stop(self):
        self._flag.set()
        self._thread.join()

CHECK="check"
DOWNLOAD="download"
def on_check(event:Event):
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{event.type_}] 现在时间：{now}")
    return Event(DOWNLOAD,data="fake_stream_url")
def on_download(event:Event):
    print(f"[{event.type_}] 开始处理任务,数据：{event.data}")
    time.sleep(0.5)
    print(f"[{event.type_}] 处理完成")
def main():
    manager=EventManger()
    manager.add_event_listener(CHECK,on_check)
    manager.add_event_listener(DOWNLOAD,on_download)
    manager.start()
    timer =Timer(func=lambda:manager.send_event(Event(CHECK)),interval=3)
    timer.start()
    time.sleep(12)
    timer.stop()
    print("定时器关机")
if __name__=="__main__":
    main()
