from __future__ import print_function
from colorama import init, Fore, Style
from datetime import datetime
from time import sleep
import supermgr
import threading
import pprint
import sys
import json
import os
import argparse
import tailer

pp = pprint.PrettyPrinter(indent=4)

SAVE_FILE           = '/tmp/__supermgr_status.json'
_STAT_OK            = 0
_STAT_WARN          = 1
_STAT_CRIT          = 2
_STAT_UNKNOWN       = 3

# http://supervisord.org/subprocess.html#process-states
_STATE_TRANS        = ('STARTING', 'STOPPING', 'BACKOFF')
_STATE_RUNNING      = ('RUNNING',)
_STATE_STOPPED      = ('STOPPED', 'EXITED', 'FATAL')
_STATE_FATAL        = ('FATAL',)
_STATE_UNKNOWN      = ('UNKNOWN',)

def color(val, color):
    return '{0}{1}{2}'.format(color, val, Style.RESET_ALL)

def format_state(state_name):
    if state_name in _STATE_RUNNING:
        state = color(state_name, Fore.GREEN)
    elif state_name in _STATE_FATAL:
        state = color(state_name, Fore.RED + Style.BRIGHT)
    elif state_name in _STATE_TRANS:
        state = color(state_name, Fore.YELLOW)
    elif state_name in _STATE_UNKNOWN:
        state = color(state_name, Fore.WHITE + Style.BRIGHT)
    else:
        state = color(state_name, Fore.RED)

    return state

def display_workers(workers, prgm=None, full=False):
    prgm_not_found = []
    if prgm:
        for p in prgm:
            if p not in workers:
                prgm_not_found.append('{e}: no workers found for {p}'.format(
                    e=color('ERROR', Fore.RED + Style.BRIGHT),
                    p=color(p, Fore.CYAN + Style.BRIGHT)))

    for name, status in workers.items():
        print(color(name, Fore.CYAN + Style.BRIGHT))
        for p, s in status.items():
            print('\t{0}: {1}'.format(p, format_state(s.get('statename'))))
            if full is True:
                for k, v in s.items():
                    if k not in ('group', 'name'):
                        if k in ('start', 'stop', 'now'):
                            v = datetime.fromtimestamp(int(v)).strftime('%Y-%m-%d %H:%M:%S')
                        print('\t\t{0}: {1}'.format(k, v))

    if prgm_not_found:
        print('\n'.join(nf for nf in prgm_not_found))
        return False

    return True

def tail_log(worker, prgm, filetype=None):
    logkey = 'stdout_logfile' if (filetype is None or filetype == 'out') else 'stderr_logfile'

    try:
        index = worker.get(prgm).keys()[0]
        logfile = worker.get(prgm)[index].get(logkey)
    except IndexError:
        print('{e}: Unable to find a suitable log file'.format(e=color('ERROR', Fore.RED + Style.BRIGHT)))
        return False

    try:
        for line in tailer.follow(open(logfile)):
            print(line)
    except KeyboardInterrupt:
        print()

    return True

def monitor_workers(workers, target_state=_STATE_RUNNING[0], ignore=None):
    errors = []
    for name, status in workers.items():
        if ignore is not None and name in ignore:
            continue
        is_ok = False
        for num, data in status.items():
            if data.get('statename').upper() == target_state.upper():
                is_ok = True

        if not is_ok:
            errors.append('{pgm} does not have any processes in the {tgt} state!'.format(pgm=name, tgt=target_state))

    if len(errors) > 0:
        print('\n'.join(e for e in errors))
        return False

    return True

def save_state(workers, filename):
    try:
        with open(filename, 'w') as f:
            f.write(json.dumps(workers))
        print(color('Saved current worker status to: {f}'.format(f=filename), Fore.CYAN + Style.BRIGHT))
        return True
    except IOError as e:
        print(os.strerror(e.errno), file=sys.stderr)
        print('Tried to open {f} for writing'.format(f=filename), file=sys.stderr)
        return False

def reload_state(filename):
    print(color('Attempting to return workers to a previously saved state', Fore.YELLOW + Style.BRIGHT))
    try:
        with open(filename, 'r') as f:
            try:
                workers = json.loads(f.read())
            except ValueError as e:
                print(color(e, Fore.RED + Style.BRIGHT), file=sys.stderr)
                print('{e}: Perhaps \'save\' did not work? Check the contents of {f}'.format(
                    e=color('ERROR', Fore.RED + Style.BRIGHT), f=filename), file=sys.stderr)
                return False
    except IOError as e:
        print(color(os.strerror(e.errno), Fore.RED + Style.BRIGHT), file=sys.stderr)
        print('{e}: Tried to open {f} for reading'.format(e=color('ERROR', Fore.RED + Style.BRIGHT), f=filename),
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
        if workers[prgm] is None:
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
            # @TODO: see Action - handle dict return status
            if not a.ret_status:
                stat = color('FAILED', Fore.RED + Style.BRIGHT)
                found_error = True
            else:
                stat = color('OK', Fore.GREEN)
            print('{name}:{num} {action} - {stat}'.format(
                name=color(a.name, Fore.CYAN + Style.BRIGHT),
                num=a.num,
                action=a.action,
                stat=stat))

    return not found_error

def main():

    state_choices = [s.lower() for s in list(set(_STATE_RUNNING + _STATE_FATAL + _STATE_STOPPED + _STATE_TRANS + _STATE_UNKNOWN))]

    def usage():
        ex = (
            (color('Start the first "prgmName" not found to be running', Fore.WHITE + Style.BRIGHT),
                'supermgr --start prgmName'),
            (color('Start process number 3 and 5 of "prgmName"', Fore.WHITE + Style.BRIGHT),
                'supermgr --start prgmName 3 5'),
            (color('Start all "prgmName" processes', Fore.WHITE + Style.BRIGHT),
                'supermgr --start prgmName all'),
            (color('List all processes', Fore.WHITE + Style.BRIGHT),
                'supermgr --list'),
            (color('List only fatal processes', Fore.WHITE + Style.BRIGHT),
             'supermgr --list --state fatal'),
            (color('List full status for the running processes for "prgmName"', Fore.WHITE + Style.BRIGHT),
                'supermgr --list prgmName --full --state running'),
            (color('Tail the stdout logfile for "prgmName"', Fore.WHITE + Style.BRIGHT),
                'supermgr --tail prgmName'),
            (color('Tail the stderr logfile for "prgmName"', Fore.WHITE + Style.BRIGHT),
             'supermgr --tail prgmName err')
        )
        return '\n' + '\n'.join(['    %s\n    %s\n' % (e[0], e[1]) for e in ex])

    __prgm_desc = color('Management interface for supervisorctl', Fore.CYAN + Style.BRIGHT)
    parser = argparse.ArgumentParser(description=__prgm_desc,
                                     formatter_class=argparse.ArgumentDefaultsHelpFormatter,
                                     usage=usage())

    main_grp        = parser.add_argument_group(color('Actions', Fore.YELLOW + Style.BRIGHT))
    list_grp        = parser.add_argument_group(color('List Modifiers', Fore.YELLOW + Style.BRIGHT))
    monitor_grp     = parser.add_argument_group(color('Monitoring Options', Fore.YELLOW + Style.BRIGHT))

    start_stop_grp  = main_grp.add_mutually_exclusive_group()
    save_reload_grp = main_grp.add_mutually_exclusive_group()

    start_stop_grp.add_argument('-s', '--start', dest='start', nargs='+',
                        help='Start a process by number, the next process not started, or all of them')
    start_stop_grp.add_argument('-S', '--stop', dest='stop', nargs='+',
                        help='Stop a process by number, the next process not stopped, or all of them')
    start_stop_grp.add_argument('--restart', dest='restart', nargs='+',
                        help='Restart a process by number, the next process found running, or all. ' + \
                        'WARNING: If the process specified is NOT running, this will attempt to start it')

    save_reload_grp.add_argument('--save', dest='save', type=str, const=SAVE_FILE, nargs='?',
                        help='Save the current state of each process group and number')
    save_reload_grp.add_argument('--reload', dest='reload', type=str, const=SAVE_FILE, nargs='?',
                        help='Reload the state of each group and process from a saved status')

    main_grp.add_argument('-l', '--list', dest='list', nargs='*',
                        help='List all groups and processes. Optionally show a specific group')
    main_grp.add_argument('-t', '--tail', dest='tail', nargs='+',
                        help='Tail a process\'s logfile. If the type (err, out) is not provided this will default to stdout')

    list_grp.add_argument('-r', '--running', dest='running', action='store_true',
                        help='DEPRECATED: please use --state')
    list_grp.add_argument('--state', dest='state', nargs=1, choices=state_choices,
                        help='Only show processes in the specified state')
    list_grp.add_argument('-f', '--full', dest='full', action='store_true',
                        help='Show full status of processes')

    monitor_grp.add_argument('--monitor-running', dest='monitor_running', action='store_true',
                        help='Check for any processes not running')
    monitor_grp.add_argument('--ignore', dest='mon_ignore', nargs='+',
                        help='Exclude any process groups from the monitoring check')

    args        = parser.parse_args()
    connection  = supermgr.get_config()

    if args.running:
        print('{e}: --running is deprecated. use "--state running" instead'.format(e=color('ERROR', Fore.RED + Style.BRIGHT)))
        sys.exit(0)

    if args.mon_ignore and not args.monitor_running:
        print('{e}: --ignore is only used with --monitor-running'.format(e=color('ERROR', Fore.RED + Style.BRIGHT)))
        sys.exit(1)

    # It should (or I think it should) be possible to use a subparser for this, but I couldn't
    # quite get it to behave correctly.
    if (args.full or args.state) and args.list is None:
        print('{e}: --full, and --state only apply to -l, --list'.format(e=color('ERROR', Fore.RED + Style.BRIGHT)))
        sys.exit(0)

    if args.tail:
        w       = supermgr.Worker(connection)
        prgm    = args.tail.pop(0)
        worker  = w.get_workers(prgm)
        try:
            filetype = args.tail[0]
        except IndexError:
            filetype = 'out'
        if tail_log(worker, prgm, filetype):
            sys.exit(_STAT_OK)

        sys.exit(_STAT_WARN)

    if args.save:
        w = supermgr.Worker(connection)
        if not save_state(w.get_workers(), args.save):
            sys.exit(_STAT_WARN)
        sys.exit(_STAT_OK)

    if args.reload:
        if not reload_state(args.reload):
            sys.exit(_STAT_WARN)
        sys.exit(_STAT_OK)

    if args.monitor_running:
        w = supermgr.Worker(connection)
        if not monitor_workers(w.get_workers(), ignore=args.mon_ignore):
            sys.exit(_STAT_WARN)
        print('Check complete!')
        sys.exit(_STAT_OK)

    if args.list is not None:
        w = supermgr.Worker(connection)
        _filter_state = None
        if args.state:
            _filter_state = args.state[0].upper()
        if not display_workers(w.get_workers(args.list, _filter_state), args.list, args.full):
            sys.exit(_STAT_WARN)
        sys.exit(_STAT_OK)

    if args.restart:
        items       = args.restart
        pgm_name    = items.pop(0)

        if not items:
            items.append('')

        if handle_action('stop', pgm_name, items):
            sleep(1)
            if handle_action('start', pgm_name, items):
                sys.exit(_STAT_OK)

        sys.exit(_STAT_WARN)

    if args.start or args.stop:
        if args.start:
            items = args.start
            _action = 'start'
        else:
            items = args.stop
            _action = 'stop'

        pgm_name = items.pop(0)

        if not items:
            items.append('')

        if not handle_action(_action, pgm_name, items):
            sys.exit(_STAT_CRIT)

        sys.exit(_STAT_OK)

    parser.print_help()

