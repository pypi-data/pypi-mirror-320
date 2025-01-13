import re
import sys
from subprocess import check_output

try:
    from typing import TYPE_CHECKING
except ImportError:
    TYPE_CHECKING = False

if TYPE_CHECKING:
    # ruff: noqa: F401 = Union is actually used for typing below
    from typing import Union

import pluggy


hookimpl = pluggy.HookimplMarker('tox')

RX = (
    re.compile(r'^(?P<impl>py)(?P<maj>[23])(?P<min>[0-9][0-9]?)$'),
    re.compile(r'^(?P<impl>py)(?P<maj>3)(?P<min>[0-9][0-9])(?P<suffix>t)$'),
)


@hookimpl
def tox_get_python_executable(envconfig):  # type: ignore
    """Return a python executable for the given python base name."""
    for rx in RX:
        match = rx.match(envconfig.envname)
        if match is not None:
            return get_python_path(envconfig.envname)
    return None


def get_python_path(tag):  # type: (str) -> Union[str, None]
    # get path
    try:
        # ruff: noqa: S603 = allow check_output with arbitrary cmdline
        # ruff: noqa: S607 = py is on path, specific location is not guaranteed
        out = check_output(['py', 'bin', '--path', tag])
        enc = sys.getfilesystemencoding()
        path = (out.decode() if enc is None else out.decode(enc)).strip()
        if not path:
            return None
    except Exception:
        return None
    return path
