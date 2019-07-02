"""Common code and class interfaces."""

import argparse
import atexit
import logging
import os
import pytz
import sys
from pathlib import Path
from typing import Callable, NamedTuple, Optional

import numpy
import google.protobuf.json_format
import vpython

from orbitx import orbitx_pb2 as protos
from orbitx import state


# Frequently-used entity names are here as constants. You can use string
# literals instead, but that's more prone to mipsellings.
HABITAT = 'Habitat'
AYSE = 'AYSE'
SUN = 'Sun'
EARTH = 'Earth'

DEFAULT_PORT = 28430

TIME_BETWEEN_NETWORK_UPDATES = 1.0

FRAMERATE = 100

DEFAULT_TIME_ACC = 1

DEFAULT_CENTRE = HABITAT
DEFAULT_REFERENCE = EARTH
DEFAULT_TARGET = AYSE

# Graphics-related constants
DEFAULT_UP = vpython.vector(0, 0.1, 1)
DEFAULT_FORWARD = vpython.vector(0, 0, -1)

MIN_THROTTLE = -1.00  # -100%
MAX_THROTTLE = 1  # 100%

# The max speed at which the autopilot will spin the craft
AUTOPILOT_SPEED = numpy.radians(20)

# The margin on either side of the target heading that the autopilot will slow
# down its adjustments
AUTOPILOT_FINE_CONTROL_RADIUS = numpy.radians(5)

DRAG_PROFILE = 0.0002

G = 6.674e-11

# The thrust-weight ratio required for liftoff. Realistically, the TWR only has
# to be greater than 1 to lift off, but we want to make sure there aren't any
# possible collisions that will set the engines to 0 again.
LAUNCH_TWR = 1.05

TIMEZONE = pytz.timezone('Canada/Eastern')

PERF_FILE = 'flamegraph-data.log'

# Set up a logger.
# Log DEBUG and higher to the logfile,
# Log WARNING and higher to stdout.
logging.getLogger().setLevel(logging.DEBUG)
logging.captureWarnings(True)

debug_formatter = logging.Formatter(
    '{asctime} {levelname}\t{module}.{funcName}: {message}',
    datefmt='%X',  # The timestamp is just the time of day
    style='{'
)

print_formatter = logging.Formatter(
    '{levelname} {module}.{funcName}:\t{message}',
    datefmt='%X',  # The timestamp is just the time of day
    style='{'
)

# When changing output streams, consider that jupyter appmode, which is an easy
# way to give demos, will only show the stdout and not the stderr of a process.
print_handler = logging.StreamHandler(stream=sys.stdout)
print_handler.setLevel(logging.WARNING)
print_handler.setFormatter(print_formatter)


def print_handler_cleanup():
    logfile_handler.close()
    try:
        os.remove(logfile_handler.baseFilename)
    except FileNotFoundError:
        pass


# The logfile will be deleted on program exit, unless this is unregistered.
atexit.register(print_handler_cleanup)

# TODO: put logs in a directory
logfile_handler = logging.FileHandler(
    f'debug-{os.getpid()}.log', mode='w', delay=True)
logfile_handler.setLevel(logging.DEBUG)
logfile_handler.setFormatter(debug_formatter)

logging.getLogger().handlers = []
logging.getLogger().addHandler(print_handler)
logging.getLogger().addHandler(logfile_handler)


def enable_verbose_logging():
    """Enables logging of all messages to stdout, from DEBUG upwards"""
    print_handler.setLevel(logging.DEBUG)


def savefile(name: str) -> Path:
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


def format_num(num: Optional[float], unit: str) -> str:
    """This should be refactored with the Menu class after symposium."""
    # TODO: refactor this along with the Menu class
    # This return string will be at most 10 characters
    if num is None:
        return ''
    return '{:,.5g}'.format(round(num)) + unit


def load_savefile(file: Path) -> 'state.PhysicsState':
    logging.getLogger().info(f'Loading savefile {file.resolve()}')
    with open(file, 'r') as f:
        data = f.read()
    read_state = protos.PhysicalState()
    google.protobuf.json_format.Parse(data, read_state)

    if read_state.time_acc == 0:
        read_state.time_acc = DEFAULT_TIME_ACC
    if read_state.reference == '':
        read_state.reference = DEFAULT_REFERENCE
    if read_state.target == '':
        read_state.target = DEFAULT_TARGET
    return state.PhysicsState(None, read_state)


def write_savefile(state: 'state.PhysicsState', file: Path):
    logging.getLogger().info(f'Saving to savefile {file.resolve()}')
    with open(file, 'w') as outfile:
        outfile.write(
            google.protobuf.json_format.MessageToJson(state.as_proto()))


def start_profiling():
    # TODO: codify my workflow for profiling graphics vs simulation code.
    # Basically, profiling graphics is done by using dev tools of whatever
    # browser (in Firefox, F12 > Performance > Start Recording Performance)
    # And profiling python simulation code is done by running this function,
    # then processing PERF_FILE with https://github.com/brendangregg/FlameGraph
    # The command is, without appropriate paths, is:
    # dos2unix PERF_FILE && flamegraph.pl PERF_FILE > orbitx-perf.svg
    # Where flamegraph.pl is from that brendangregg repo.
    import flamegraph
    flamegraph.start_profile_thread(
        fd=open(PERF_FILE, 'w'),
        filter=r'(simthread|MainThread)'
    )


class Program(NamedTuple):
    main: Callable[[argparse.Namespace], None]
    name: str
    description: str
    argparser: argparse.ArgumentParser
