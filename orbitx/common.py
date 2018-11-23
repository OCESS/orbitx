"""Common code and class interfaces."""
import logging
import sys
from pathlib import Path

import google.protobuf.json_format

from . import orbitx_pb2 as protos


DEFAULT_LEAD_SERVER_HOST = 'localhost'
DEFAULT_LEAD_SERVER_PORT = 28430

FRAMERATE = 100
TICK_TIME = 1/FRAMERATE

DEFAULT_TIME_ACC = 1

CHEAT_FUEL = 0

# Set up a logger.
# Log DEBUG and higher to stderr,
# Log WARNING and higher to stdout.
logging.getLogger().setLevel(logging.DEBUG)
logging.captureWarnings(True)

formatter = logging.Formatter(
    '{asctime} {levelname} {module}.{funcName}: {message}',
    datefmt='%X',  # Just the time
    style='{')

# When changing output streams, consider that jupyter appmode, which is an easy
# way to give demos, will only show the stdout and not the stderr of a process.
handler = logging.StreamHandler(stream=sys.stdout)
handler.setLevel(logging.ERROR)
handler.setFormatter(formatter)
logging.getLogger().handlers = []
logging.getLogger().addHandler(handler)


def enable_verbose_logging():
    """Enables logging of all messages, from DEBUG upwards"""
    handler.setLevel(logging.DEBUG)


def savefile(name):
    return PROGRAM_PATH / 'data' / 'saves' / name


if getattr(sys, 'frozen', False):
    # We're running from a PyInstaller exe, use the path of the exe
    PROGRAM_PATH = Path(sys.executable).parent
elif sys.path[0] == '':
    # We're running from a Python REPL. For information on what sys.path[0]
    # means, read https://docs.python.org/3/library/sys.html#sys.path
    # note path[0] == '' means Python is running as an interpreter.
    PROGRAM_PATH = Path.cwd()
else:
    Path(sys.path[0]).parent


class GrpcServerContext:
    """Context manager for a GRPC server."""

    def __init__(self, server):
        self._server = server

    def __enter__(self):
        pass

    def __exit__(self, *args):
        self._server.stop(0)


def load_savefile(file):
    with open(file, 'r') as f:
        data = f.read()
    read_state = protos.PhysicalState()
    google.protobuf.json_format.Parse(data, read_state)
    return read_state


def write_savefile(physical_state, file):
    with open(file, 'w') as outfile:
        outfile.write(
            google.protobuf.json_format.MessageToJson(physical_state))
