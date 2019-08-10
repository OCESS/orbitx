"""Provides write_state_to_osbackup. Contains no state."""

import logging
import random
import string
import struct
from datetime import datetime
from pathlib import Path
from typing import List

import numpy

from orbitx import calc
from orbitx import common
from orbitx import network
from orbitx import orbitx_pb2 as protos
from orbitx import state

log = logging.getLogger()

_last_orbitsse_modified_time = 0.0


# This is an ordered list of names that are internal to OrbitV.
# Sometimes OrbitV references a numeric index, e.g. ORBITSSE.RND Zvar[13],
# and we can convert that numeric index into an entity name using this list.
ORBITV_NAMES = [
    "Sun", "Mercury", "Venus", "Earth", "Mars", "Jupiter", "Saturn", "Uranus",
    "Neptune", "Pluto", "Moon", "Phobos", "Hyperion", "Io", "Europa",
    "Ganymede", "Callisto", "Enceldus", "Dione", "Rhea", "Titan", "Iapatus",
    "Thethys", "Mimas", "Titania", "Oberon", "Triton", "Charon", "Habitat",
    "Ceres", "DAWN", "Vesta", "AYSE", "Cassini", "C 103P H", "ISS", "Module",
    "OCESS", "PROBE", "unknown"
]  # Likely off by one, TODO: test that

# This is a mapping from the OrbitX NAVMODE enum to a value of "Sflag",
# which is internal to OrbitV.
NAVMODE_TO_SFLAG = {  # type: ignore
    protos.CCW_PROG: 0,
    protos.CW_RETRO: 4,
    protos.MANUAL: 1,
    protos.APP_TARG: 2,
    protos.PRO_VTRG: 5,
    protos.RETR_VTRG: 7,
    # Hold Atrg should be here, but OrbitX doesn't implement it lol.
    protos.DEPRT_REF: 3,
}

# Converts from an OrbitX Enum representation of the module state to
# the OrbitV variable MODULEflag.
MODSTATE_TO_MODFLAG = {
    network.Request.NO_MODULE: 0,
    network.Request.DOCKED_MODULE: 1,
    network.Request.DETACHED_MODULE: 2
}
MODFLAG_TO_MODSTATE = {v: k for k, v in MODSTATE_TO_MODFLAG.items()}


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
    assert orbitx_state.craft

    hab = orbitx_state[common.HABITAT]
    ayse = orbitx_state[common.AYSE]
    craft = orbitx_state.craft_entity()
    max_thrust = common.craft_capabilities[craft.name].thrust
    timestamp = datetime.fromtimestamp(orbitx_state.timestamp)
    check_byte = random.choice(string.ascii_letters).encode('ascii')
    target = (orbitx_state.target
              if orbitx_state.target in ORBITV_NAMES
              else "AYSE")
    reference = (orbitx_state.reference
                 if orbitx_state.reference in ORBITV_NAMES
                 else "Earth")
    atmosphere = calc.relevant_atmosphere(orbitx_state)
    if atmosphere is None:
        pressure = 0.0
    else:
        pressure = calc.pressure(craft, atmosphere)
    craft_thrust = max_thrust * craft.throttle * \
        calc.heading_vector(craft.heading)
    craft_drag = calc.drag(orbitx_state)
    artificial_gravity = numpy.linalg.norm(craft_thrust - craft_drag)

    with open(osbackup_path, 'r+b') as osbackup:
        # We replicate the logic of orbit5v.bas:1182 (look for label 800)
        # in the below code. OSBACKUP.RND is a binary, fixed-width field file.
        # orbit5v.bas writes to it every second, and it's created in the same
        # way as any OrbitV save file.
        # If you're reading the orbit5v.bas source code, note that arrays and
        # strings in QB are 1-indexed not 0-indexed.

        osbackup.write(check_byte)
        osbackup.write("ORBIT5S        ".encode('ascii'))
        # OrbitX keeps throttle as a float, where 100% = 1.0
        # OrbitV expects 100% = 100.0
        _write_single(100 * max(hab.throttle, ayse.throttle), osbackup)

        # vflag todo
        _write_int(0, osbackup)
        # Aflag todo
        _write_int(0, osbackup)
        _write_int(NAVMODE_TO_SFLAG[orbitx_state.navmode.value], osbackup)
        _write_double(numpy.linalg.norm(calc.drag(orbitx_state)), osbackup)
        _write_double(25, osbackup)  # This is a sane value for OrbitV zoom.
        # TODO: check if this is off by 90 degrees or something.
        _write_single(hab.heading, osbackup)
        _write_int(ORBITV_NAMES.index("Habitat"), osbackup)  # Centre the hab.
        _write_int(ORBITV_NAMES.index(target), osbackup)
        _write_int(ORBITV_NAMES.index(reference), osbackup)

        _write_int(0, osbackup)  # Set trails to off.
        #_write_single(0, osbackup)  # To do with rotation malfunctions??
        _write_single(0.006 if orbitx_state.parachute_deployed else 0.002,
                      osbackup)
        _write_single((common.SRB_THRUST / 100)
                      if orbitx_state.srb_time > 0 else 0, osbackup)
        _write_int(0, osbackup)  # No colour-coded trails.

        # Valid values of this are 0, 1, 2.
        # A value of 1 gets OrbitV to display EST timestamps.
        _write_int(1, osbackup)
        _write_double(0.125, osbackup)  # Set timestep to the slowest.
        _write_double(0.125, osbackup)  # This is OLDts, also slowest value.
        _write_single(0, osbackup)  # Something to do with RSCP, just zero it.
        _write_int(0, osbackup)  # Eflag? Something that gassimv.bas sets.

        _write_int(timestamp.year, osbackup)
        # QB uses day-of-the-year instead of day-of-the-month.
        _write_int(int(timestamp.strftime('%j')), osbackup)
        _write_int(timestamp.hour, osbackup)
        _write_int(timestamp.minute, osbackup)
        _write_double(timestamp.second, osbackup)

        _write_single(ayse.heading, osbackup)
        _write_int(0, osbackup)  # AYSEscrape seemingly does nothing.

        # TODO: Once we implement wind, fill in these fields.
        _write_single(0, osbackup)
        _write_single(0, osbackup)

        _write_single(numpy.degrees(hab.spin), osbackup)
        _write_int(150 if hab.landed_on == common.AYSE else 0, osbackup)
        _write_single(0, osbackup)  # Rad shields, overwritten by enghabv.bas.
        _write_int(MODSTATE_TO_MODFLAG[network.Request.DETACHED_MODULE]
                   if common.MODULE in orbitx_state._entity_names
                   else MODSTATE_TO_MODFLAG[network.Request.NO_MODULE],
                   osbackup)

        # These next two variables are technically AYSEdist and OCESSdist
        # but they're used for engineering to determine if you can load fuel
        # from OCESS or AYSE. Also, if you can dock with AYSE. So we just tell
        # engineering if we're landed, but don't tell it any more deets.
        _write_single(150 if hab.landed_on == common.AYSE else 1000, osbackup)
        _write_single(150 if hab.landed_on == common.EARTH else 1000, osbackup)

        _write_int(hab.broken, osbackup)  # I think this is an explosion flag.
        _write_int(ayse.broken, osbackup)  # Same as above.

        # TODO: Once we implement nav malfunctions, set this field.
        _write_single(0, osbackup)

        _write_single(max_thrust, osbackup)

        # TODO: Once we implement nav malfunctions, set this field.
        # Also, apparently this is the same field as two fields ago?
        _write_single(0, osbackup)

        # TODO: Once we implement wind, fill in these fields.
        _write_long(0, osbackup)

        # TODO: There is some information required from MST.rnd to implement
        # this field (LONGtarg).
        _write_single(0, osbackup)

        _write_single(pressure, osbackup)
        _write_single(artificial_gravity, osbackup)

        for i in range(0, 39):
            try:
                entity = orbitx_state[ORBITV_NAMES[i]]
                x, y = entity.pos
                vx, vy = entity.v
            except ValueError:
                log.error(f"Tried to write position of {ORBITV_NAMES[i]} "
                          "to OSBACKUP.rnd, but OrbitX does not recognize "
                          "this name!")
                x = y = vx = vy = 0
            _write_double(x, osbackup)
            _write_double(y, osbackup)
            _write_double(vx, osbackup)
            _write_double(vy, osbackup)

        _write_single(hab.fuel, osbackup)
        _write_single(ayse.fuel, osbackup)

        osbackup.write(check_byte)


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

    command.engineering_update.nav_malfunction = round(Zvar[0])
    command.engineering_update.max_thrust = Zvar[1]
    command.engineering_update.hab_fuel = Zvar[2]
    command.engineering_update.ayse_fuel = Zvar[3]
    command.engineering_update.hab_meltdown = bool(Zvar[4])
    command.engineering_update.ayse_meltdown = bool(Zvar[5])
    command.engineering_update.module_state = \
        MODFLAG_TO_MODSTATE[round(Zvar[6])]
    command.engineering_update.radar = bool(2 & round(Zvar[7]))
    command.engineering_update.ins = bool(4 & round(Zvar[7]))
    command.engineering_update.los = bool(8 & round(Zvar[7]))
    # Zvar[8] is related to whether rad shields are on, but isn't used.
    # Zvar[9] has something to do with parachute or SRBs?
    # Zvar[10] and [11] are not referenced anywhere.
    # Zvar[12] is just if AYSE is connected?? unsure.
    command.engineering_update.wind_source_entity = \
        ORBITV_NAMES[round(Zvar[13])]
    command.engineering_update.wind_speed = Zvar[14]
    command.engineering_update.wind_angle = Zvar[15]
    # Zvar[16] is something to do with a ufo?
    # It's called 'Zufo' in orbi5vs.bas:392.
    # later Zvar values look like a bunch of UFO-related stuff.

    return command


def _write_int(integer: int, file):
    return file.write(integer.to_bytes(2, byteorder='little'))


def _write_long(lon: int, file):
    return file.write(lon.to_bytes(4, byteorder='little'))


def _write_single(single: float, file):
    return file.write(struct.pack("<f", single))


def _write_double(double: float, file):
    return file.write(struct.pack("<d", double))


def _read_int(file) -> int:
    return int.from_bytes(file.read(2), byteorder='little')


def _read_long(lon: int, file):
    return int.from_bytes(file.read(4), byteorder='little')


def _read_single(file) -> float:
    return struct.unpack("<f", file.read(4))[0]


def _read_double(file) -> float:
    return struct.unpack("<d", file.read(8))[0]
