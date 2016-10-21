from .server import Server
import threading

class Action(threading.Thread):
    def __init__(self, server, action, name, num, thread_lock):
        super(Action, self).__init__()
        self.action         = action
        self.name           = name
        self.num            = num
        self.thread_lock    = thread_lock
        self.error          = False
        self.ret_status     = None
        self.server         = server

    def run(self):
        # Get lock to synchronize threads
        self.thread_lock.acquire(False)

        if self.action == 'start':
            self.start_process()

        if self.action == 'stop':
            self.stop_process()

        # Free lock to release next thread
        if self.thread_lock.locked():
            self.thread_lock.release()

    def start_process(self):
        if self.num == '*':
            # Not used yet.
            self.ret_status = self.server.supervisor.startProcessGroup('{name}'.format(name=self.name))
        else:
            self.ret_status = self.server.supervisor.startProcess('{name}:{num}'.format(name=self.name, num=self.num))

    def stop_process(self):
        if self.num == '*':
            # Not used yet.
            self.ret_status = self.server.supervisor.stopProcessGroup('{name}'.format(name=self.name))
        else:
            self.ret_status = self.server.supervisor.stopProcess('{name}:{num}'.format(name=self.name, num=self.num))
