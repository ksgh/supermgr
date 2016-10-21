from __future__ import print_function
from socket import error as socket_error
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

