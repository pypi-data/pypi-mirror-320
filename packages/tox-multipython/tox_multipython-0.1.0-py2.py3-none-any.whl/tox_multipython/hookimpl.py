import os.path
import re

import pluggy


hookimpl = pluggy.HookimplMarker('tox')

MULTIPYTHON_PATH_ROOT = '/usr/local/bin'
RX = (
    re.compile(r'^(?P<impl>py)(?P<maj>[23])(?P<min>[0-9][0-9]?)$'),
    re.compile(r'^(?P<impl>py)(?P<maj>3)(?P<min>[0-9][0-9])(?P<suffix>t)$'),
)


@hookimpl
def tox_get_python_executable(envconfig):  # type: ignore
    """Return a python executable for the given python base name."""
    match = None
    for rx in RX:
        match = rx.match(envconfig.envname)
        if match is not None:
            break

    if match is None:
        return None

    g = match.groupdict()
    g['suffix'] = g.get('suffix', '')
    name = {'py': 'python'}[g['impl']]
    command = '{name}{maj}.{min}{suffix}'.format(name=name, **g)
    proposed = MULTIPYTHON_PATH_ROOT + '/' + command
    if not os.path.exists(proposed):
        proposed = None  # type: ignore[assignment]

    return proposed
