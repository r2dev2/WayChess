"""
Garbage collect all of the completed threading.Thread
"""
import gc
from threading import Thread
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
        print("started thread")
        self.threads.append(thread)

    
    def run(self):
        while not self.is_exiting:
            i = 0
            while i < len(self.threads):
                if not self.threads[i].is_alive():
                    self.threads.pop(i)
                    gc.collect()
                    # continue doesn't work
                    i = len(self.threads)+1
            sleep(1)


class GUI:
    def create_thread_manager(self):
        def end():
            nonlocal self
            try:
                return self.is_exiting
            except AttributeError:
                return False
        self.t_manager = GCService(end)

