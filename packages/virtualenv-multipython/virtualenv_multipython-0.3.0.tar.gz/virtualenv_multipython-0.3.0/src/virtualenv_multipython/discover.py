import re
from subprocess import check_output

try:
    from typing import TYPE_CHECKING, Union
except ImportError:
    TYPE_CHECKING = False

# ruff: noqa: F401
if TYPE_CHECKING:
    import argparse  # type: ignore[unused-ignore]

from virtualenv.discovery.builtin import Builtin  # type: ignore
from virtualenv.discovery.discover import Discover  # type: ignore
from virtualenv.discovery.py_info import PythonInfo  # type: ignore


RX = (
    re.compile(r'^(?P<impl>py)(?P<maj>[23])(?P<min>[0-9][0-9]?)$'),
    re.compile(r'^(?P<impl>py)(?P<maj>3)(?P<min>[0-9][0-9])(?P<suffix>t)$'),
)


class Multipython(Discover):  # type: ignore[misc]
    def __init__(self, options):  # type: (argparse.Namespace) -> None
        super(Multipython, self).__init__(options)
        self.python = options.python
        self.tox_env = options.env.get('TOX_ENV_NAME')

    @classmethod
    def add_parser_arguments(cls, parser):  # type: (argparse.ArgumentParser) -> None
        Builtin.add_parser_arguments(parser)

    def run(self):  # type: () -> Union[PythonInfo, None]
        requests = [self.tox_env] if self.tox_env else []
        requests.extend(self.python)
        for python in requests:
            for rx in RX:
                if rx.match(python):
                    info = self.get_python_info(python)
                    if info:
                        return info

        return None

    def get_python_info(self, tag):  # type: (str) -> Union[PythonInfo, None]
        # get path
        try:
            # ruff: noqa: S603 = allow check_output with arbitrary cmdline
            # ruff: noqa: S607 = py is on path, specific location is not guaranteed
            path = check_output(['py', 'bin', '--path', tag]).decode('utf-8').strip()
            if not path:
                return None
        except Exception:
            return None
        # get info
        try:
            return PythonInfo.from_exe(path, resolve_to_host=False)
        except Exception:
            return None
