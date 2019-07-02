"""Provides write_state_to_osbackup. Contains no state."""

import struct
from datetime import datetime
from os import SEEK_CUR, SEEK_SET
from pathlib import Path
from typing import List

from orbitx import common
from orbitx import state
from orbitx import network

_last_orbitsse_modified_time = 0.0


def write_state_to_osbackup(
    orbitx_state: state.PhysicsState,
    osbackup_path: Path
) -> None:
    """Writes information to OSbackup.RND.

    Currently only writes information relevant to engineering, but if we want
    to communicate piloting state to other legacy orbit programs we can write
    other kinds of information. I found out what information I should be
    writing here by reading the source for engineering (enghabv.bas) and seeing
    what information it reads from OSbackup.RND"""

    hab = orbitx_state[common.HABITAT]
    ayse = orbitx_state[common.AYSE]

    with open(osbackup_path, 'r+b') as osbackup:
        # See enghabv.bas at label 813 (around line 1500) for where these
        # offsets into osbackup.rnd come from.
        # Note that the MID$ function in QB is 1-indexed, instead of 0-indexed.
        osbackup.seek(2 + 15 - 1, SEEK_SET)
        # OrbitX keeps throttle as a float, where 100% = 1.0
        # OrbitV expecteds 100% = 100.0
        _write_single(100 * max(hab.throttle, ayse.throttle), osbackup)

        osbackup.seek(68, SEEK_CUR)
        timestamp = datetime.fromtimestamp(orbitx_state.timestamp)
        _write_int(timestamp.year, osbackup)
        # QB uses day-of-the-year instead of day-of-the-month.
        _write_int(int(timestamp.strftime('%j')), osbackup)
        _write_int(timestamp.hour, osbackup)
        _write_int(timestamp.minute, osbackup)
        _write_double(timestamp.second, osbackup)

        osbackup.seek(24, SEEK_CUR)
        _write_int('Module' in orbitx_state._entity_names, osbackup)
        # These next two variables are technically AYSEdist and OCESSdist
        # but they're used for engineering to determine if you can load fuel
        # from OCESS or AYSE. Also, if you can dock with AYSE. So we just tell
        # engineering if we're landed, but don't tell it any more deets.
        _write_single(150 if hab.landed_on == common.AYSE else 1000, osbackup)
        _write_single(150 if hab.landed_on == common.EARTH else 1000, osbackup)

        osbackup.seek(24, SEEK_CUR)
        # pressure = cvs(mid$(inpSTR$,k,4)):k=k+4
        # Accel# = cvs(mid$(inpSTR$,k,4)):k=k+4


def read_update_from_orbitsse(orbitsse_path: Path) -> network.Request:
    global _last_orbitsse_modified_time
    command = network.Request(ident=network.Request.ENGINEERING_UPDATE)
    with open(orbitsse_path, 'rb') as orbitsse:

        orbitsse_modified_time = orbitsse_path.stat().st_mtime
        if orbitsse_modified_time == _last_orbitsse_modified_time:
            # We've already seen this version of ORBITSSE.RND, return early.
            return network.Request(ident=network.Request.NOOP)
        else:
            _last_orbitsse_modified_time = orbitsse_modified_time

        # See enghabv.bas at label 820 to find out what data is written at what
        # offsets in orbitsse.rnd
        orbitsse.seek(1)  # Skip CHKbyte

        # This list mirrors Zvar in enghabv.bas, or Ztel in orbit5v
        Zvar: List[float] = []
        for _ in range(0, 26):
            Zvar.append(_read_double(orbitsse))

    command.engineering_update.max_thrust = Zvar[1]
    command.engineering_update.hab_fuel = Zvar[2]
    command.engineering_update.ayse_fuel = Zvar[3]
    return command


def _write_int(integer: int, file):
    return file.write(integer.to_bytes(2, byteorder='little'))


def _write_single(single: float, file):
    return file.write(struct.pack("<f", single))


def _write_double(double: float, file):
    return file.write(struct.pack("<d", double))


def _read_int(file) -> int:
    return int.from_bytes(file.read(2), byteorder='little')


def _read_single(file) -> float:
    return struct.unpack("<f", file.read(4))[0]


def _read_double(file) -> float:
    return struct.unpack("<d", file.read(8))[0]
