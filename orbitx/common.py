"""Common code and class interfaces."""

import logging
import sys
from pathlib import Path

import google.protobuf.json_format

from . import orbitx_pb2 as protos


DEFAULT_LEAD_SERVER_HOST = 'localhost'
DEFAULT_LEAD_SERVER_PORT = 28430

FRAMERATE = 100

DEFAULT_TIME_ACC = 1

CHEAT_FUEL = 0

MIN_THROTTLE = -0.2
MAX_THROTTLE = 1.2

DEBUG_LOGFILE = 'debug.log'
PERF_FILE = 'flamegraph-data.log'

# Set up a logger.
# Log DEBUG and higher to stderr,
# Log WARNING and higher to stdout.
logging.getLogger().setLevel(logging.DEBUG)
logging.captureWarnings(True)

debug_formatter = logging.Formatter(
    '{asctime} {levelname}\t{module}.{funcName}: {message}',
    datefmt='%X',  # The timestamp is just the time of day
    style='{'
)

print_formatter = logging.Formatter(
    '{levelname}:\t{message}',  # Less information clutter, for stdout/stderr
    datefmt='%X',  # The timestamp is just the time of day
    style='{'
)

# When changing output streams, consider that jupyter appmode, which is an easy
# way to give demos, will only show the stdout and not the stderr of a process.
print_handler = logging.StreamHandler(stream=sys.stdout)
print_handler.setLevel(logging.ERROR)
print_handler.setFormatter(print_formatter)

logfile_handler = logging.FileHandler(DEBUG_LOGFILE, mode='w', delay=True)
logfile_handler.setLevel(logging.DEBUG)
logfile_handler.setFormatter(debug_formatter)

logging.getLogger().handlers = []
logging.getLogger().addHandler(print_handler)
logging.getLogger().addHandler(logfile_handler)


def enable_verbose_logging():
    """Enables logging of all messages, from DEBUG upwards"""
    print_handler.setLevel(logging.DEBUG)


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
    PROGRAM_PATH = Path(sys.path[0])


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


def find_entity(name, physical_state):
    return [entity for entity in physical_state.entities
            if entity.name == name][0]


_profile_thread = None


def start_profiling():
    import flamegraph
    global _profile_thread
    _profile_thread = flamegraph.start_profile_thread(
        fd=open(PERF_FILE, 'w'))
