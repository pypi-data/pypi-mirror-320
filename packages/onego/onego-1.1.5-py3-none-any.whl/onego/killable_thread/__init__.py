import ctypes
import threading

class KillableThread(threading.Thread):
    def __init__(self, group=None, target=None, name=None, args=(), kwargs=None, *, daemon=None):
        super().__init__(group=group, target=target, name=name, args=args, kwargs=kwargs, daemon=daemon)

    def get_id(self):
        if hasattr(self, '_thread_id'): return self._thread_id
        for id, thread in threading._active.items():
            if thread is self: return id

    def kill(self):
        thread_id = self.get_id()
        res = ctypes.pythonapi.PyThreadState_SetAsyncExc(thread_id, ctypes.py_object(SystemExit))
        if res > 1: ctypes.pythonapi.PyThreadState_SetAsyncExc(thread_id, 0)
