"""Functions for communicating to clients that are interested in us.

As a recap, this entire program tries to keep communication consistent
between legacy (i.e. file-based IPC between QBasic programs written by Dr.
Magwood) and Ivan's new node.js-based project.

This module is for supporting communication to Ivan's new node.js-based
piloting client, and hopefully other clients.
"""
# Possible optimizations:
# - Look at msgpack documentation for ways to optimize serialization.
# - Only update from STARSr and other input files if they have been written
#   to since our last update.
# - Find out what changed between updates, and only update that.
# - Read huge chunks of the file at the same time.
# - Read different files in their own threads

import csv
from collections import namedtuple
import numbers
import msgpack
from pathlib import Path

from orbitx.compat import utility

_BackgroundStar = namedtuple('BackgroundStar',
                             ['colour', 'x', 'y'])
_PVA = namedtuple('PVA',  # PVA: Position, Velocity, Acceleration
                  ['POSx', 'POSy', 'VELx', 'VELy', 'ACCx', 'ACCy'])

_EntityImmutables = \
    namedtuple('EntityImmutables',
               ['name', 'colour', 'mass', 'radius',
                'atmosphere_density', 'atmosphere_height', 'wtf'])


def _sanitize_float_str(str):
    """Sanitize and convert QBasic string floats.

    QBasic string representations of doubles have # appended,
    or sometimes a D instead of an E in x.xxxE+k form.
    """
    return float(str.replace('#', '').replace('D', 'E'))


class Piloting:
    """Keeps track piloting state, and can serialize the contained data.

    Parses the STARSr file, which contains almost all state that
    Dr. Magwood's piloting code uses. Once the file has been parsed, you can
    use this class to serialize the data, ready for sending over a network.

    Example usage:
    piloting = Piloting()
    piloting.parse_from_starsr("./STARSr")
    sending_function(piloting.serialize())
    """

    def __init__(self, starsr_path):
        """Save the path to STARSr for use in parsing functions."""
        self._starsr_path = Path(starsr_path) / 'STARSr'

    def __repr__(self):
        """Representation of current state -- verbose."""
        return (
            "Piloting(starsr_path={!r}, "
            "_startup_state={!r}, "
            "_piloting_state={!r})"
            .format(self._starsr_path,
                    self._startup_state,
                    self._piloting_state))

    def __str__(self):
        """String of current state -- verbose."""
        return (
            "Piloting(starsr_path={!s}, "
            "_startup_state={!s}, "
            "_piloting_state={!s})"
            .format(self._starsr_path,
                    self._startup_state,
                    self._piloting_state))

    def pack_immutables(self):
        """Return a msgpack'd version of the immutable data."""
        return msgpack.packb(self._startup_state)

    def pack_mutables(self):
        """Return a msgpack'd version of the mutable data."""
        return msgpack.packb(self._piloting_state)

    def startup_parse_starsr(self):
        """Read and interpret fields from STARSr at startup.

        This is used to read fields that will not change over the course
        of the simulation. For example, entity names and background stars.
        """
        self._startup_state = {"background_stars": [],
                               "insignificant_pairs": [],
                               "entities": []}
        with self._starsr_path.open('r', newline='') as starsr_file:
            data_reader = csv.reader(starsr_file)
            for row_number, row in enumerate(data_reader):
                if 0 <= row_number and row_number < 3021:
                    # Background stars
                    assert len(row) == 3
                    colour = utility.colour_code_to_rgb(int(row[0]))
                    x = _sanitize_float_str(row[1])
                    y = _sanitize_float_str(row[2])
                    assert isinstance(x, numbers.Real)
                    assert isinstance(y, numbers.Real)
                    self._startup_state["background_stars"].append(
                        _BackgroundStar(colour, x, y))
                elif 3021 <= row_number and row_number < 3262:
                    # Pairs of objects that don't significantly attract
                    # TODO: Make sure the pairs of objects are deterministic
                    assert len(row) == 2
                    first = int(row[0].replace('X', ''))
                    second = int(row[1].replace('X', ''))
                    assert first >= 0
                    assert second >= 0
                    self._startup_state["insignificant_pairs"].append(
                        (first, second))
                elif 3262 <= row_number and row_number < 3302:
                    # Colour, mass, radius, atmosphere properties
                    assert len(row) == 6
                    colour = utility.colour_code_to_rgb(int(row[0]))
                    mass = _sanitize_float_str(row[1])
                    radius = int(row[2])
                    atmosphere_density = _sanitize_float_str(row[3])
                    atmosphere_height = _sanitize_float_str(row[4])
                    wtf = int(row[5])
                    assert mass >= 0
                    assert radius > 0
                    assert atmosphere_density >= 0
                    assert atmosphere_height >= 0
                    self._startup_state["entities"].append(_EntityImmutables(
                        'placeholder', colour, mass, radius,
                        atmosphere_density, atmosphere_height, wtf))
                elif 3302 <= row_number and row_number < 3339:
                    # Date and time, and also displacement, velocity,
                    # acceleration vectors. These change during operation.
                    pass
                elif 3339 <= row_number and row_number < 3379:
                    # Entity names, add to existing entities
                    assert len(row) == 1
                    self._startup_state["entities"][row_number - 3339] = (
                        self._startup_state["entities"][row_number - 3339]
                        ._replace(name=row[0].strip()))
                else:
                    # Here we get a bunch of things that seem to be used
                    # for drawing OCESS control tower or other objects.
                    break

    def parse_from_starsr(self):
        """Read and interpret raw bytes from STARSr file.

        I determine what fields mean what by looking at the sourcecode
        for orbit5v.bas. You can see my chicken-scratching understanding
        in notes/orbit-notes.
        """
        self._piloting_state = {"datetime": 0.0,
                                "locations": []}
        with self._starsr_path.open('r', newline='') as starsr_file:
            data_reader = csv.reader(starsr_file)
            for row_number, row in enumerate(data_reader):
                if 3302 == row_number:
                    # Date and time
                    assert len(row) == 5
                    year = int(row[0])
                    yday = int(row[1])
                    hour = int(row[2])
                    minute = int(row[3])
                    doublesecond = _sanitize_float_str(row[4])
                    # Float of seconds since epoch
                    self._piloting_state["datetime"] = (
                        utility.qb_time_to_datetime(
                            year, yday, hour, minute, doublesecond)
                        .timestamp())
                elif 3303 <= row_number and row_number < 3339:
                    # Position, Velocity, Acceleration
                    assert len(row) == 6
                    self._piloting_state["locations"].append(
                        _PVA(*map(_sanitize_float_str, row)))
