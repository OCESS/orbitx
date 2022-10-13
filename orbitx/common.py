# -*- coding: utf-8 -*-
"""Common code and class interfaces."""

import atexit
import logging
import pytz
from enum import Enum
from io import StringIO
from pathlib import Path
from typing import NamedTuple, Optional

import numpy
import vpython  # type: ignore

from orbitx import orbitx_pb2 as protos
from orbitx import strings

TIME_BETWEEN_NETWORK_UPDATES = 1.0

FRAMERATE = 60


class TimeAcc(NamedTuple):
    """Represents a single value of time acc."""
    value: int
    desc: str
    # The acceleration above which this time acc starts to be too inaccurate.
    accurate_bound: float


class OhmicVars(NamedTuple):
    """
    Encapsulates a Voltage, Current, and Resistance where V = IR.
    This class is called 'Ohmic' because it's all the things for Ohm's law.
    I don't think Ohmic is a word. I made it up. I like to think it sounds cool.
    """
    voltage: float
    current: float
    resistance: float


# Make sure this is in sync with the corresponding enum in orbitx.proto!
Navmode = Enum('Navmode', zip([  # type: ignore
    'Manual', 'CCW Prograde', 'CW Retrograde', 'Depart Reference',
    'Approach Target', 'Pro Targ Velocity', 'Anti Targ Velocity'
], protos.Navmode.values()))


# If you change the 'Pause' element of this list, change the corresponding
# JS code in flight_gui_footer.html also.
TIME_ACCS = [
    TimeAcc(value=0, desc='Pause', accurate_bound=10000),
    TimeAcc(value=1, desc='1×', accurate_bound=1000),
    TimeAcc(value=5, desc='5×', accurate_bound=12),
    TimeAcc(value=10, desc='10×', accurate_bound=9),
    TimeAcc(value=50, desc='50×', accurate_bound=7),
    TimeAcc(value=100, desc='100×', accurate_bound=5),
    TimeAcc(value=1_000, desc='1,000×', accurate_bound=3),
    TimeAcc(value=10_000, desc='10,000×', accurate_bound=1),
    TimeAcc(value=100_000, desc='100,000×', accurate_bound=0.1)
]

DEFAULT_INITIAL_TIMESTAMP = 1.0
DEFAULT_TIME_ACC = TIME_ACCS[1]
assert DEFAULT_TIME_ACC.value != 0

# ---------------- Graphics-related constants ---------------
DEFAULT_CENTRE = strings.HABITAT
DEFAULT_REFERENCE = strings.EARTH
DEFAULT_TARGET = strings.AYSE

DEFAULT_UP = vpython.vector(0, 0.1, 1)
DEFAULT_FORWARD = vpython.vector(0, 0, -1)

TIMEZONE = pytz.timezone('Canada/Eastern')

# ---------------- Physics-related constants ----------------
G = 6.674e-11

SRB_THRUST = 13_125_000

HAB_DRAG_PROFILE = 0.0002
PARACHUTE_DRAG_PROFILE = 0.02

UNDOCK_PUSH = 0.5  # Undocking gives a 0.5 m/s push

# The thrust-weight ratio required for liftoff. Realistically, the TWR only has
# to be greater than 1 to lift off, but we want to make sure there aren't any
# possible collisions that will set the engines to 0 again.
LAUNCH_TWR = 1.05
# Note: a LAUNCH_TWR of 1.05 implies that you probably won't be able to lift off
# a planet if hovering requires 97% engines. Hopefully you don't regularly go to
# planets like this.


class Spacecraft(NamedTuple):
    """Represents the capabilities of different craft."""
    fuel_cons: float  # Fuel consumption in kg/s at 100% engines.
    thrust: float  # Thrust in N at 100% engines.
    hull_strength: float  # Max m/s impact the craft can take.


# These numbers taken from orbit5vm.bas.
craft_capabilities = {
    strings.HABITAT: Spacecraft(fuel_cons=4.824, thrust=4375000, hull_strength=50),
    strings.AYSE: Spacecraft(fuel_cons=17.55, thrust=6.4e9, hull_strength=100)
}

# ---------------- Control-related constants ----------------
MIN_THROTTLE = -1.00  # -100%
MAX_THROTTLE = 1.00  # 100%

# The max speed at which the autopilot will spin the craft.
AUTOPILOT_SPEED = numpy.radians(20)

# The margin on either side of the target heading that the autopilot will slow
# down its adjustments.
AUTOPILOT_FINE_CONTROL_RADIUS = numpy.radians(5)

# Rotating the craft changes the spin by this amount per button press.
SPIN_CHANGE = numpy.radians(5)  # 5 degrees per second.
FINE_SPIN_CHANGE = numpy.radians(0.5)  # Half a degree per second.

# Rotating the craft changes the spin by this amount per button press.
SPIN_CHANGE = numpy.radians(5)  # 5 degrees per second.
FINE_SPIN_CHANGE = numpy.radians(0.5)  # Half a degree per second.

# These special values mean that the SRBs are full but haven't been used, and
# that the SRBs have been fully used, respectively.
SRB_FULL = -1
SRB_EMPTY = -2
SRB_BURNTIME = 120  # 120s of burntime.


# ---------------- Engineering-related constants ----------------------

N_COMPONENTS = len(strings.COMPONENT_NAMES)
N_COOLANT_LOOPS = len(strings.COOLANT_LOOP_NAMES)
N_RADIATORS = len(strings.RADIATOR_NAMES)

DANGEROUS_REACTOR_TEMP = 110  # We can change this later


# ---------- Other runtime functions and constants ----------
PERF_FILE = 'flamegraph-data.log'

# This Request class is just an alias of the Command protobuf message. We
# provide this so that nobody has to directly import orbitx_pb2, and so that
# we can this wrapper class in the future.
Request = protos.Command

def format_num(num: Optional[float], unit: str,
               *, decimals: Optional[int] = None) -> str:
    """This should be refactored with the Menu class after symposium."""
    # This return string will be at most 10 characters
    if num is None:
        return ''
    return '{:,.5g}'.format(round(num, ndigits=decimals)) + unit


def start_flamegraphing():
    # TODO: codify my workflow for profiling graphics vs simulation code.
    # Basically, profiling graphics is done by using dev tools of whatever
    # browser (in Firefox, F12 > Performance > Start Recording Performance)
    # And profiling python simulation code is done by running this function,
    # then processing PERF_FILE with https://github.com/brendangregg/FlameGraph
    # The command is:
    # dos2unix flamegraph-data.log; perl flamegraph.pl flamegraph-data.log > orbitx-perf.svg
    # Where flamegraph.pl is from that brendangregg repo.
    from flamegraph import flamegraph
    t = flamegraph.ProfileThread(
        fd=open(PERF_FILE, 'w'),
        interval=0.001,
        filter=r'simthread'
    )
    t.start()

    def cleanup():
        t.stop()
        t.join()
    atexit.register(cleanup)


def start_profiling():
    # This will show the performance impact of each function.
    # If you want to see the performance impact of each _line_ in a function,
    # pip install line_profiler
    # and add @profile annotations to functions of interest, then run kernprof
    # as described in the line_profiler package.
    import yappi
    yappi.set_clock_type('cpu')
    yappi.start()
    atexit.register(_dump_profiling_stats)


def _dump_profiling_stats():
    import yappi
    # To find out what functions have the biggest impact on performance,
    # sort by 'tsub' or 'ttot'. Docs are here:
    # https://github.com/sumerc/yappi/blob/master/doc/api.md#yfuncstat

    # Only print the first bunch of lines of yappi output.
    yappi.stop()
    yappi_output = StringIO()
    yappi.get_func_stats().sort('tsub').print_all(out=yappi_output)
    for line in yappi_output.getvalue().split('\n')[0:30]:
        print(line)


def remove_vpython_css():
    """Remove the inline per-element styling that vpython adds."""
    vpython.canvas.get_selected().append_to_caption("""<script>
        for (const element of document.querySelectorAll(
                "div, input, select, button, span")) {
            float_backup = element.style.float;
            element.removeAttribute('style');
            element.style.float = float_backup;
        }
    </script>""")


def include_vpython_footer_file(footer_path: Path):
    """Append the contents of a file to the vpython caption.
    Useful for including HTML or CSS files."""
    with open(footer_path) as footer:
        vpython.canvas.get_selected().append_to_caption(footer.read())
