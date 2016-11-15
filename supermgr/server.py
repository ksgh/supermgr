from __future__ import print_function
from socket import error as socket_error
from collections import defaultdict, OrderedDict
import errno
import xmlrpclib
import sys

class Server(object):
    def __init__(self, connect_opts):
        self.host   = connect_opts.get('host')
        self.port   = connect_opts.get('port')
        self.server = None
        self.__connect()

    def get_server(self):
        return self.server

    def __connect(self):
        url = 'http://{host}:{port}/RPC2'.format(host=self.host, port=self.port)
        try:
            self.server = xmlrpclib.Server(url)
            self.server._()
        except xmlrpclib.Fault:
            # expected - method doesn't exist
            pass
        except socket_error as serr:
            self.server = None
            if serr.errno != errno.ECONNREFUSED:
                raise serr
            else:
                print('Unable to connect to {url}, check your connection settings.'.format(url=url), file=sys.stderr)

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
