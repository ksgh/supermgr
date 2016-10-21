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

    def get_workers(self, group_name=None):
        data    = self.server.supervisor.getAllProcessInfo()
        workers = defaultdict(dict)

        for info in data:
            _data = {info.get('name'): info}
            workers[info.get('group')].update(_data)

        for n, d in workers.items():
            workers[n] = OrderedDict(sorted(d.items(), key=lambda k: k[0]))

        if group_name:
            self.workers = {group_name: workers.get(group_name)}
        else:
            self.workers = OrderedDict(sorted(workers.items(), key=lambda k: k[0]))

        return self.workers

    def get_server(self):
        return self.server

