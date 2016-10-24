from __future__ import print_function
from colorama import init, Fore, Style
from collections import OrderedDict
import supermgr
import threading
import pprint
import sys
import json
import os

pp = pprint.PrettyPrinter(indent=4)

VALID_ACTIONS       = OrderedDict()

VALID_ACTIONS['list-actions']     = 'List available actions'
VALID_ACTIONS['list']             = 'Print a list of all known process groups and the status of each process'
VALID_ACTIONS['full-list']        = 'Same as \'list\', but also print all the information we have on each process'
VALID_ACTIONS['status']           = 'Same as \'list\''
VALID_ACTIONS['full-status']      = 'Same as \'full-list\''
VALID_ACTIONS['start']            = 'Start a process by number, the next process not started, or all of them'
VALID_ACTIONS['stop']             = 'Stop a process by number, the next process not stopped, or all of them'
VALID_ACTIONS['save']             = 'Save the current state of each process group and number'
VALID_ACTIONS['reload']           = 'Reload the state of each group and process from a saved status'
VALID_ACTIONS['monitor-running']  = 'Check for any processes not running'

SAVE_FILE           = '/tmp/__supermgr_status.json'
_STAT_OK            = 0
_STAT_WARN          = 1
_STAT_CRIT          = 2
_STAT_UNKNOWN       = 3

_STATE_RUNNING      = ('RUNNING',)
_STATE_STOPPED      = ('STOPPED', 'EXITED', 'FATAL')
_STATE_FATAL        = ('FATAL',)

def color(val, color):
    return '{0}{1}{2}'.format(color, val, Style.RESET_ALL)

def worker_list(workers, prgm=None, full=False):

    if not workers[prgm]:
        print('{e}: no workers found'.format(e=color('ERROR', Fore.RED + Style.BRIGHT)))
        return False

    for name, status in workers.items():
        print(color(name, Fore.CYAN + Style.BRIGHT))
        for p, s in status.items():
            sn = s.get('statename').upper()
            if sn in _STATE_RUNNING:
                state = color(s['statename'], Fore.GREEN)
            elif sn in _STATE_FATAL:
                state = color(s['statename'], Fore.RED + Style.BRIGHT)
            else:
                state = color(s['statename'], Fore.RED)
            print('\t{0}: {1}'.format(p, state))
            if full == True:
                for k, v in s.items():
                    if k not in ('group', 'name'):
                        print('\t\t{0}: {1}'.format(k, v))

    return True

def monitor_workers(workers, target_state=_STATE_RUNNING[0]):
    errors = []
    for name, status in workers.items():
        is_ok = False
        for num, data in status.items():
            if data.get('statename').upper() == target_state.upper():
                is_ok = True

        if not is_ok:
            errors.append('{pgm} does not have any processes in the {tgt} state!'.format(pgm=name, tgt=target_state))

    if len(errors) > 0:
        for e in errors:
            print(e)
        return False

    return True

def save_state(workers):
    try:
        with open(SAVE_FILE, 'w') as f:
            f.write(json.dumps(workers))
        print(color('Saved current worker status to: {f}'.format(f=SAVE_FILE), Fore.CYAN + Style.BRIGHT))
        return True
    except IOError as e:
        print(os.strerror(e.errno), file=sys.stderr)
        print('Tried to open {f} for writing'.format(f=SAVE_FILE), file=sys.stderr)
        return False

def reload_state():
    print(color('Attempting to return workers to a previously saved state', Fore.YELLOW + Style.BRIGHT))
    try:
        with open(SAVE_FILE, 'r') as f:
            try:
                workers = json.loads(f.read())
            except ValueError as e:
                print(color(e, Fore.RED + Style.BRIGHT), file=sys.stderr)
                print('{e}: Perhaps \'save\' did not work? Check the contents of {f}'.format(
                    e=color('ERROR', Fore.RED + Style.BRIGHT), f=SAVE_FILE), file=sys.stderr)
                return False
    except IOError as e:
        print(color(os.strerror(e.errno), Fore.RED + Style.BRIGHT), file=sys.stderr)
        print('{e}: Tried to open {f} for reading'.format(e=color('ERROR', Fore.RED + Style.BRIGHT), f=SAVE_FILE),
              file=sys.stderr)
        return False

    # basically if it was running, we'll attempt to start it, otherwise the action is stop.
    stat_map = {
        'RUNNING': 'start'
    }

    # default return status of handle_action to true, and set to false if one or more fail
    action_status = True

    for name, status in workers.items():
        for pnum, pstat in status.items():
            try:
                run_stat = stat_map[pstat.get('statename')]
            except KeyError:
                run_stat = 'stop'

            if not handle_action(run_stat, name, (pnum,)):
                action_status = False

    return action_status

def handle_action(action, prgm, nums):
    conn        = supermgr.get_config()
    tl          = threading.Lock()
    w           = supermgr.Worker(conn)
    a_threads   = []
    found_error = False
    stat_map    = {
        'start': _STATE_RUNNING,
        'stop': _STATE_STOPPED,
    }

    if nums[0] == 'all':
        nums[0] = '*'
    if nums[0] == '':
        nums[0] = '+'

    if prgm.lower() == 'all':
        workers = w.get_workers()
    else:
        workers = w.get_workers(prgm)
        if workers[prgm] == None:
            print('{e}: no workers found'.format(e=color('ERROR', Fore.RED + Style.BRIGHT)))
            return False

    for g, data in workers.items():
        perform = []
        for pnum, stats in data.items():
            if nums[0] == '*':
                if stats['statename'] in stat_map[action]:
                    print('{name}:{num} is already {state}'.format(name=g, num=pnum, state=stats['statename']))
                    continue
                perform.append(pnum)
            elif nums[0] == '+':
                if not perform:
                    if stats['statename'] not in stat_map[action]:
                        perform.append(pnum)
            else:
                for n in nums:
                    if pnum == n and stats['statename'] not in stat_map[action] and pnum not in perform:
                        perform.append(n)
                    else:
                        if pnum == n:
                            print(color('{name}:{num} is already {stat}'.format(name=g, num=n, stat=stats['statename']),
                                        Fore.MAGENTA))
                            continue
        if perform:
            for n in perform:
                server = supermgr.Server(conn).get_server()
                act = supermgr.Action(server, action, g, n, tl)
                act.start()
                a_threads.append(act)
        elif nums[0] == '*':
            print(color(
                'All {name} processes appear to be in the desired state: {action}'.format(name=g, action=action),
                Fore.WHITE + Style.BRIGHT))

    if a_threads:
        for a in a_threads:
            a.join()
            if not a.ret_status:
                print('{name}:{num} {action} - {stat}'.format(
                    name=color(a.name, Fore.CYAN + Style.BRIGHT),
                    num=a.num,
                    action=a.action,
                    stat=color('FAILED', Fore.RED + Style.BRIGHT)))
                found_error = True
            else:
                print('{name}:{num} {action} - {stat}'.format(
                    name=color(a.name, Fore.CYAN + Style.BRIGHT),
                    num=a.num,
                    action=a.action,
                    stat=color('OK', Fore.GREEN)))

    return not found_error

def main():
    connection  = supermgr.get_config()
    num         = ''
    pgm_name    = None

    try:
        action = sys.argv[1]
    except IndexError:
        print('{e}: an action is required'.format(e=color('ERROR', Fore.RED)), file=sys.stderr)
        #usage()
        sys.exit(_STAT_UNKNOWN)

    if action == 'list-actions' or not VALID_ACTIONS.get(action):
        if action.startswith('-h') or action.startswith('--h') or action.endswith('help'):
            #usage()
            sys.exit(_STAT_OK)

        if action != 'list-actions':
            print('{e}: {a} is not a valid action'.format(e=color('ERROR', Fore.RED), a=action), file=sys.stderr)
        print('Available actions are:')
        _fmt = '     {act:<30}{desc:60}'
        for key, desc in VALID_ACTIONS.items():
            print(_fmt.format(act=color(key, Fore.YELLOW), desc=desc))
        sys.exit(_STAT_UNKNOWN)

    try:
        pgm_name = sys.argv[2]
    except IndexError:
        pass

    try:
        num = sys.argv[3]
    except IndexError:
        pass

    if action == 'save':
        w = supermgr.Worker(connection)
        if not save_state(w.get_workers()):
            sys.exit(_STAT_WARN)
        sys.exit(_STAT_OK)

    if action == 'reload':
        if not reload_state():
            sys.exit(_STAT_WARN)
        sys.exit(_STAT_OK)

    if action == 'monitor-running':
        w = supermgr.Worker(connection)
        if not monitor_workers(w.get_workers()):
            sys.exit(_STAT_WARN)
        print('Check complete!')
        sys.exit(_STAT_OK)

    if action in ('list', 'status', 'full-list', 'full-status'):
        full_list = False
        if action.startswith('full-'):
            full_list = True
        w = supermgr.Worker(connection)
        if not worker_list(w.get_workers(pgm_name), pgm_name, full_list):
            sys.exit(_STAT_WARN)
        sys.exit(_STAT_OK)

    if action in ('start', 'stop'):
        if not pgm_name:
            print('A program/group name is required')
            sys.exit(_STAT_WARN)

        p_nums = num.split(',')

        if not handle_action(action, pgm_name, p_nums):
            sys.exit(_STAT_CRIT)

        sys.exit(_STAT_OK)

