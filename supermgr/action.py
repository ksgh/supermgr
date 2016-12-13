import threading

class Action(threading.Thread):
    def __init__(self, action, worker, thread_lock):
        super(Action, self).__init__()
        self.action         = action
        self.worker         = worker
        self.thread_lock    = thread_lock
        self.error          = False
        self.ret_status     = None

    def run(self):
        # Get lock to synchronize threads
        self.thread_lock.acquire(False)

        if self.action == 'start':
            self.ret_status = self.worker.w_start()

        if self.action == 'stop':
            self.ret_status = self.worker.w_stop()

        # Free lock to release next thread
        if self.thread_lock.locked():
            try:
                self.thread_lock.release()
            except:
                pass

