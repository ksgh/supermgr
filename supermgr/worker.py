#!/usr/bin/env python

from .server import Server
from collections import defaultdict, OrderedDict
import xmlrpclib
import sys

class Worker(Server):
    def __init__(self, connect_opts):
        super(Worker, self).__init__(connect_opts)
        self.workers = None

        if not isinstance(self.server, xmlrpclib.Server):
            sys.exit(2)

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

