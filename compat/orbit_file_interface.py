"""Provides write_state_to_osbackup. Contains no state."""

import struct
from datetime import datetime
from os import SEEK_CUR, SEEK_SET
from pathlib import Path
from typing import List

from numpy.linalg import norm

import orbitx.orbitx_pb2 as protos
from orbitx.physics_entity import PhysicsEntity


def write_state_to_osbackup(
    orbitx_state: protos.PhysicalState,
    osbackup_path: Path
) -> None:
    """Writes information to OSbackup.RND.

    Currently only writes information relevant to engineering, but if we want
    to communicate piloting state to other legacy orbit programs we can write
    other kinds of information. I found out what information I should be
    writing here by reading the source for engineering (enghabv.bas) and seeing
    what information it reads from OSbackup.RND"""

    names = [entity.name for entity in orbitx_state.entities]
    hab = _name_to_entity('Habitat', names, orbitx_state)
    ayse = _name_to_entity('AYSE', names, orbitx_state)
    earth = _name_to_entity('Earth', names, orbitx_state)

    with open(osbackup_path, 'r+b') as osbackup:
        # See enghabv.bas at label 813 (around line 1500) for where these
        # offsets into osbackup.rnd come from.
        # Note that the MID$ function in QB is 1-indexed, instead of 0-indexed.
        osbackup.seek(2 + 15 - 1, SEEK_SET)
        osbackup.write(_mks(max(hab.throttle, ayse.throttle)))

        osbackup.seek(68, SEEK_CUR)
        timestamp = datetime.fromtimestamp(orbitx_state.timestamp)
        osbackup.write(_mki(timestamp.year))
        # QB uses day-of-the-year instead of day-of-the-month.
        osbackup.write(_mki(int(timestamp.strftime('%j'))))
        osbackup.write(_mki(timestamp.hour))
        osbackup.write(_mki(timestamp.minute))
        osbackup.write(_mkd(timestamp.second))

        osbackup.seek(24, SEEK_CUR)
        osbackup.write(_mki('Module' in names))
        osbackup.write(_mks(norm(ayse.pos - hab.pos)))
        osbackup.write(_mks(norm(earth.pos - hab.pos)))

        osbackup.seek(24, SEEK_CUR)
        # pressure = cvs(mid$(inpSTR$,k,4)):k=k+4
        # Accel# = cvs(mid$(inpSTR$,k,4)):k=k+4


def _name_to_entity(
        name: str, names: List[str],
        state: protos.PhysicalState) -> PhysicsEntity:
    # TODO this should be generalized, lots of other code does this repeatedly.
    if name in names:
        return PhysicsEntity(state.entities[names.index(name)])
    else:
        return PhysicsEntity(protos.Entity())


def _mki(integer: int) -> bytes:
    return integer.to_bytes(2, byteorder='little')


def _mks(single: float) -> bytes:
    return struct.pack("<f", single)


def _mkd(double: float) -> bytes:
    return struct.pack("<d", double)
