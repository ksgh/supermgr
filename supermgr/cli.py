from __future__ import print_function
from colorama import init, Fore, Style
import supermgr
import pprint
import sys

pp = pprint.PrettyPrinter(indent=4)

VALID_ACTIONS       = ('list', 'status', 'start', 'stop', 'save', 'reload', 'monitor-running')
_STAT_OK            = 0
_STAT_WARN          = 1
_STAT_CRIT          = 2
_STAT_UNKNOWN       = 3

def color(val, color):
    return '{0}{1}{2}'.format(color, val, Style.RESET_ALL)

def worker_list(workers, prgm=None):
    for name, status in workers.items():
        print(color(name, Fore.CYAN + Style.BRIGHT))
        for p, s in status.items():
            s = color(s['statename'], Fore.GREEN) if s['statename'] == 'RUNNING' else color(s['statename'], Fore.RED)
            print('\t{0}: {1}'.format(p, s))

def main():
    w = supermgr.Worker()

    try:
        action = sys.argv[1]
    except IndexError:
        print('{e}: an action is required'.format(e=color('ERROR', Fore.RED)), file=sys.stderr)
        #usage()
        sys.exit(_STAT_UNKNOWN)

    if action in ('list', 'status'):
        pgm_name = None
        try:
            pgm_name = sys.argv[2]
        except IndexError:
            pass

        worker_list(w.get_workers(pgm_name), pgm_name)

        sys.exit(_STAT_OK)



    #pp.pprint(w.get_workers())
