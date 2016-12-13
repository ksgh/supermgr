from collections import defaultdict, OrderedDict

from .server import Server
from .worker import Worker

def __filter_workers(worker, filter=None):
    if filter is not None:
        if worker.statename == filter:
            return {worker.name: worker}
    else:
        return {worker.name: worker}

    return None

def get_workers(group_names=None, filter_state=None):
    data = Server().get_server().supervisor.getAllProcessInfo()
    workers = defaultdict(dict)

    if group_names is not None and not isinstance(group_names, list):
        group_names = [group_names]

    for info in data:
        w = Worker(info)
        if group_names:
            if w.group in group_names:
                _data = __filter_workers(w, filter_state)
                if _data:
                    workers[w.group].update(_data)
        else:
            _data = __filter_workers(w, filter_state)
            if _data:
                workers[w.group].update(_data)

    for n, d in workers.items():
        workers[n] = OrderedDict(sorted(d.items(), key=lambda k: k[0]))

    workers = OrderedDict(sorted(workers.items(), key=lambda k: k[0]))

    return workers