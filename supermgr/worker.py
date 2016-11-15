from .server import Server
from collections import defaultdict, OrderedDict
import datetime
import xmlrpclib
import sys

'''
{
"activity": {
    "0": {
        "now": 1478724612,
        "group": "activity",
        "description": "pid 27522, uptime 3:52:14",
        "pid": 27522,
        "stderr_logfile": "/var/log/jazz/workers/activity.err.log",
        "stop": 1478526313,
        "statename": "RUNNING",
        "start": 1478710678,
        "state": 20,
        "stdout_logfile": "/var/log/jazz/workers/activity.out.log",
        "logfile": "/var/log/jazz/workers/activity.out.log",
        "exitstatus": 0,
        "spawnerr": "",
        "name": "0"
    },
    "1": {
        "now": 1478724612,
        ...
    }
}
'''


class Worker():
    def __init__(self, connect_opts):
        self.now            = None
        self.name           = None
        self.group          = None
        self.description    = None
        self.pid            = None
        self.start          = None
        self.stop           = None
        self.state          = None
        self.statename      = None
        self.stderr         = None
        self.stdout_logfile = None
        self.stderr_logfile = None
        self.logfile        = None
        self.exitstatus     = None
        self.spawnerr       = None


    def start(self):

    def __filter_workers(self, worker, filter=None):
        if filter is not None:
            if worker.get('statename') == filter:
                return {worker.get('name'): worker}
        else:
            return {worker.get('name'): worker}

        return None

    def get_workers(self, group_names=None, filter_state=None):
        data    = self.server.supervisor.getAllProcessInfo()
        workers = defaultdict(dict)

        if group_names is not None and not isinstance(group_names, list):
            group_names = [group_names]

        for info in data:
            if group_names:
                if info.get('group') in group_names:
                    _data = self.__filter_workers(info, filter_state)
                    if _data:
                        workers[info.get('group')].update(_data)
            else:
                _data = self.__filter_workers(info, filter_state)
                if _data:
                    workers[info.get('group')].update(_data)

        for n, d in workers.items():
            workers[n] = OrderedDict(sorted(d.items(), key=lambda k: k[0]))

        self.workers = OrderedDict(sorted(workers.items(), key=lambda k: k[0]))

        return self.workers

