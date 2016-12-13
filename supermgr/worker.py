from .server import Server
import xmlrpclib

class Worker():
    now = None
    name = None
    group = None
    description = None
    pid = None
    start = None
    stop = None
    state = None
    statename = None
    stderr = None
    stdout_logfile = None
    stderr_logfile = None
    logfile = None
    exitstatus = None
    spawnerr = None

    def __init__(self, worker):
        if not isinstance(worker, dict):
            return
        for k, v in worker.items():
            setattr(self, k, v)

    def __repr__(self):
        return '<Worker: {group}:{name}>'.format(group=self.group, name=self.name)

    def as_dict(self):
        return self.__dict__

    def w_start(self):
        serv = Server().get_server()
        try:
            return serv.supervisor.startProcess('{g}:{n}'.format(g=self.group, n=self.name))
        except xmlrpclib.Fault as e:
            pass

        return False

    def w_stop(self):
        serv = Server().get_server()
        try:
            return serv.supervisor.stopProcess('{g}:{n}'.format(g=self.group, n=self.name))
        except xmlrpclib.Fault as e:
            pass

        return False




