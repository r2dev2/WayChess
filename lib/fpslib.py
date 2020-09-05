import time
from threading import Lock, Thread


class FPSMonitor(Thread):
    def __init__(self, filename="log", interval=1, *args, **kwargs):
        Thread.__init__(self, *args, **kwargs)
        self.refreshes = 0
        self.filename = filename
        self.interval = interval
        self.lock = Lock()
        self.daemon = True

    def increment(self):
        with self.lock:
            self.refreshes += 1

    def run(self):
        with open(self.filename, "w+") as fout:
            while not time.sleep(self.interval):
                print(
                    self.refreshes // self.interval, "fps", file=fout, flush=True,
                )
                self.refreshes = 0


class GUI:
    def create_fps_monitor(self):
        self.fps_monitor = FPSMonitor("log", 0.4 if self.debug else 5)
        self.fps_monitor.start()
