"""
Garbage collect all of the completed threading.Thread
"""
import gc
from queue import Queue
from threading import Lock, Thread
from time import sleep


class GCService(Thread):
    def __init__(self, endfunc, *args, **kwargs):
        """
        Constructor

        ```python
        manager = GCService(endfunc)
        manager.submit(Thread(target=int, args=('1',)))
        ```
        """
        Thread.__init__(self, *args, **kwargs)
        self._endfunc = endfunc
        self.threads = []

    @property
    def is_exiting(self):
        return self._endfunc()

    def submit(self, thread):
        thread.start()
        self.threads.append(thread)

    def run(self):
        while not self.is_exiting:
            i = 0
            while i < len(self.threads):
                if not self.threads[i].is_alive():
                    del self.threads[i]
                    gc.collect()
                    # continue doesn't work
                    i = len(self.threads) + 1
            sleep(1)


class DelayedExecution(Thread):
    def __init__(self, delay, endfunc, *args, **kwargs):
        Thread.__init__(self, *args, **kwargs)
        self.queue = Queue()
        self.daemon = True
        self.delay = delay
        self._endfunc = endfunc
        self.start()

    def submit(self, func):
        self.queue.put(func)

    def run(self):
        while not self._endfunc():
            while self.queue.qsize() > 1:
                self.queue.get()
            func = self.queue.get()
            sleep(self.delay)
            if self.queue.qsize() == 0:
                func()


class GUI:
    def program_end_flag(self):
        try:
            return self.is_exiting
        except AttributeError:
            return False

    def create_thread_manager(self):
        self.display_lock = Lock()
        self.t_manager = GCService(self.program_end_flag)
        self.d_manager = DelayedExecution(0.2, self.program_end_flag)
