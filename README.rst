supermgr
========

**Maintainer:** k dot shenk at gmail dot com

**supermgr** is merely an alternate means of managing supervisord processes. `supervisorctl` felt a bit clunky for me
while working with process groups and individual processes for a certain project. This tool connects directly to
supervisor via its XML-RPC (<http://supervisord.readthedocs.io/en/latest/api.html>) interface.

Installation
------------

**Via PIP:**
``pip install supermgr``

Usage
-----

    ::

        Start the first "prgmName" not found to be running
        supermgr --start prgmName

        Start process number 3 and 5 of "prgmName"
        supermgr --start prgmName 3 5

        Start all "prgmName" processes
        supermgr --start prgmName all

        List all processes
        supermgr --list

        List only fatal processes
        supermgr --list --state fatal

        List full status for the running processes for "prgmName"
        supermgr --list prgmName --full --state running

        Tail the stdout logfile for "prgmName"
        supermgr --tail prgmName

        Tail the stderr logfile for "prgmName"
        supermgr --tail prgmName err

        Management interface for supervisorctl

        optional arguments:
          -h, --help            show this help message and exit

        Actions:
          -s START [START ...], --start START [START ...]
                                Start a process by number, the next process not
                                started, or all of them (default: None)
          -S STOP [STOP ...], --stop STOP [STOP ...]
                                Stop a process by number, the next process not
                                stopped, or all of them (default: None)
          --restart RESTART [RESTART ...]
                                Restart a process by number, the next process found
                                running, or all. WARNING: If the process specified is
                                NOT running, this will attempt to start it (default:
                                None)
          --save [SAVE]         Save the current state of each process group and
                                number (default: None)
          --reload [RELOAD]     Reload the state of each group and process from a
                                saved status (default: None)
          -l [LIST [LIST ...]], --list [LIST [LIST ...]]
                                List all groups and processes. Optionally show a
                                specific group (default: None)

          -t TAIL [TAIL ...], --tail TAIL [TAIL ...]
                                Tail a process's logfile. If the type (err, out) is
                                not provided this will default to stdout (default:
                                None)

        List Modifiers:
          -r, --running         DEPRECATED: please use --state (default: False)
          --state {unknown,backoff,running,stopped,stopping,fatal,starting,exited}
                                Only show processes in the specified state (default:
                                None)
          -f, --full            Show full status of processes (default: False)

        Monitoring Options:
          --monitor-running     Check for any processes not running (default: False)
          --ignore MON_IGNORE [MON_IGNORE ...]
                                Exclude any process groups from the monitoring check (default: None)


When starting or stopping processes, if nothing is provided as a process number the next process number in the group's
sequence not found in the desired state will be acted upon.

Contributing
------------
Suggestions and contributions are welcome. Please fork me and create PRs back to the ``develop`` branch.

Disclaimer
----------
I'm new to creating python packages. This seemed like a good place to start learning, being a relatively small
project to bite off.
