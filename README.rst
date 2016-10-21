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
* **list-actions**: List available actions
* **list**: Print a list of all known process groups and the status of each process
* **full-list**: Same as 'list', but also print all the information we have on each process
* **status**: Same as 'list'
* **full-status**: Same as 'full-list'
* **start**: Start a process by number, the next process not started, or all of them
* **stop**: Stop a process by number, the next process not stopped, or all of them
* **save**: Save the current state of each process group and number
* **reload**: Reload the state of each group and process from a saved state
* **monitor-running**: Check for any processes not running

Contributing
------------
Suggestions and contributions are welcome. Please fork me and create PRs back to the ``develop`` branch.

Disclaimer
----------
I'm new to creating python packages. This seemed like a good place to start learning, being a relatively small
project to bite off.