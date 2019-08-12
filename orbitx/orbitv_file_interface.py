"""Provides write_state_to_osbackup. Contains no state."""

import csv
import logging
import random
import string
import struct
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional

import numpy
import scipy

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
    state.Navmode(protos.CCW_PROG): 0,
    state.Navmode(protos.CW_RETRO): 4,
    state.Navmode(protos.MANUAL): 1,
    state.Navmode(protos.APP_TARG): 2,
    state.Navmode(protos.PRO_VTRG): 5,
    state.Navmode(protos.RETR_VTRG): 6,
    # Hold Atrg should be here, but OrbitX doesn't implement it lol.
    state.Navmode(protos.DEPRT_REF): 3,
}
SFLAG_TO_NAVMODE: Dict[int, Optional[state.Navmode]]
SFLAG_TO_NAVMODE = {v: k for k, v in NAVMODE_TO_SFLAG.items()}  # type: ignore
SFLAG_TO_NAVMODE[7] = None  # This is Hold Atrg

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

        # This is Vflag and Aflag, dunno what these are.
        _write_int(0, osbackup)
        _write_int(0, osbackup)

        _write_int(NAVMODE_TO_SFLAG[orbitx_state.navmode], osbackup)
        _write_double(numpy.linalg.norm(calc.drag(orbitx_state)), osbackup)
        _write_double(25, osbackup)  # This is a sane value for OrbitV zoom.
        # TODO: check if this is off by 90 degrees or something.
        _write_single(hab.heading, osbackup)
        _write_int(ORBITV_NAMES.index("Habitat"), osbackup)  # Centre the hab.
        _write_int(ORBITV_NAMES.index(target), osbackup)
        _write_int(ORBITV_NAMES.index(reference), osbackup)

        _write_int(0, osbackup)  # Set trails to off.
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


def orbitv_to_orbitx_state(starsr_path: Path, rnd_path: Path) \
        -> state.PhysicsState:
    """Gathers information from an OrbitV savefile, in the *.RND format,
    as well as a STARSr file.
    Returns a PhysicsState representing everything we can read."""
    proto_state = protos.PhysicalState()

    hab_index: Optional[int] = None
    ayse_index: Optional[int] = None

    with open(starsr_path, 'r') as starsr_file:
        starsr = csv.reader(starsr_file, delimiter=',')

        background_star_line = next(starsr)
        while len(background_star_line) == 3:
            background_star_line = next(starsr)

        # After the last while loop, the value of background_star_line is
        # actually a gravity_pair line (a pair of indices, which we also don't
        # care about).
        gravity_pair_line = background_star_line
        while len(gravity_pair_line) == 2:
            gravity_pair_line = next(starsr)

        entity_constants_line = gravity_pair_line
        while len(entity_constants_line) == 6:
            proto_entity = proto_state.entities.add()

            # Cast all the elements on a line to floats.
            # Some strings will be the form '1.234D+04', convert these too.
            colour, mass, radius, \
                atmosphere_thickness, atmosphere_scaling, atmosphere_height \
                = map(_string_to_float, entity_constants_line)
            mass = max(1, mass)

            proto_entity.mass = mass
            proto_entity.r = radius
            if atmosphere_thickness and atmosphere_scaling:
                # Only set atmosphere fields if they both have a value.
                proto_entity.atmosphere_thickness = atmosphere_thickness
                proto_entity.atmosphere_scaling = atmosphere_scaling

            entity_constants_line = next(starsr)

        # We skip a line here. It's the timestamp line, but the .RND file will
        # have more up-to-date timestamp info.
        entity_positions_line = next(starsr)

        # We don't care about entity positions, we'll get this from the .RND
        # file as well.
        while len(entity_positions_line) == 6:
            entity_positions_line = next(starsr)

        entity_name_line = entity_positions_line
        entity_index = 0
        while len(entity_name_line) == 1:
            name = entity_name_line[0].strip()
            proto_state.entities[entity_index].name = name

            if name == common.HABITAT:
                hab_index = entity_index
            elif name == common.AYSE:
                ayse_index = entity_index

            entity_index += 1
            entity_name_line = next(starsr)

    assert proto_state.entities[0].name == common.SUN, (
        'We assume that the Sun is the first OrbitV entity, this has '
        'implications for how we populate entity positions.')
    assert hab_index is not None, \
        "We didn't see the Habitat in the STARSr file!"
    assert ayse_index is not None, \
        "We didn't see AYSE in the STARSr file!"

    hab = proto_state.entities[hab_index]
    ayse = proto_state.entities[ayse_index]

    with open(rnd_path, 'rb') as rnd:
        check_byte = rnd.read(1)
        rnd.read(len("ORBIT5S        "))
        craft_throttle = _read_single(rnd) / 100

        # I don't know what Vflag and Aflag do.
        _read_int(rnd), _read_int(rnd)
        navmode = state.Navmode(SFLAG_TO_NAVMODE[_read_int(rnd)])
        if navmode is not None:
            proto_state.navmode = navmode.value

        _read_double(rnd)  # This is drag, we calculate this ourselves.
        _read_double(rnd)  # This is zoom, we ignore this as well.
        hab.heading = _read_single(rnd)
        # Skip centre, ref, and targ information.
        _read_int(rnd), _read_int(rnd), _read_int(rnd)

        # We don't track if trails are set.
        _read_int(rnd)
        drag_profile = _read_single(rnd)
        proto_state.parachute_deployed = (drag_profile > 0.002)

        current_srb_output = _read_single(rnd)
        if current_srb_output != 0:
            proto_state.srb_time = common.SRB_BURNTIME

        # We don't care about colour trails or how times are displayed.
        _read_int(rnd), _read_int(rnd)
        _read_double(rnd), _read_double(rnd)  # No time acc info either.
        _read_single(rnd)  # Ignore some RCPS info
        _read_int(rnd)  # Eflag? Something that gassimv.bas sets.

        year = _read_int(rnd)
        day = _read_int(rnd)
        hour = _read_int(rnd)
        minute = _read_int(rnd)
        second = _read_double(rnd)

        timestamp = datetime(
            year, 1, 1, hour=hour, minute=minute, second=int(second)
        ) + timedelta(day - 1)
        proto_state.timestamp = timestamp.timestamp()

        ayse.heading = _read_single(rnd)
        _read_int(rnd)  # AYSEscrape seems to do nothing.

        # TODO: Once we implement wind, fill in these fields.
        _read_single(rnd), _read_single(rnd)

        hab.spin = numpy.radians(_read_single(rnd))
        docked_constant = _read_int(rnd)
        if docked_constant != 0:
            hab.landed_on = common.AYSE

        _read_single(rnd)  # Rad shields, overwritten by enghabv.bas.
        # TODO: once module is implemented, have it be launched here.
        _read_int(rnd)
        # module_state = MODFLAG_TO_MODSTATE[modflag]

        _read_single(rnd), _read_single(rnd)  # AYSEdist and OCESSdist.

        hab.broken = bool(_read_int(rnd))
        ayse.broken = bool(_read_int(rnd))

        # TODO: Once we implement nav malfunctions, set this field.
        _read_single(rnd)

        # Max thrust, ignored because we'll read it from ORBITSSE.rnd
        _read_single(rnd)

        # TODO: Once we implement nav malfunctions, set this field.
        # Also, apparently this is the same field as two fields ago?
        _read_single(rnd)

        # TODO: Once we implement wind, fill in these fields.
        _read_long(rnd)

        # TODO: There is some information required from MST.rnd to implement
        # this field (LONGtarg).
        _read_single(rnd)

        # We calculate pressure and agrav.
        _read_single(rnd), _read_single(rnd)
        # Note, we skip the first entity, the Sun, since OrbitV does.
        for i in range(1, min(39, len(proto_state.entities))):
            entity = proto_state.entities[i]
            entity.x, entity.y, entity.vx, entity.vy = (
                _read_double(rnd), _read_double(rnd),
                _read_double(rnd), _read_double(rnd)
            )

        hab.fuel = _read_single(rnd)
        ayse.fuel = _read_single(rnd)

        check_byte_2 = rnd.read(1)

    if check_byte != check_byte_2:
        log.warning('RND file had inconsistent check bytes: '
                    f'{check_byte} != {check_byte_2}')

    # Delete any entity with a (0, 0) position that isn't the Sun.
    # TODO: We also delete the OCESS launch tower, but once we implement
    # OCESS we should no longer do this.
    entity_index = 0
    while entity_index < len(proto_state.entities):
        proto_entity = proto_state.entities[entity_index]
        if round(proto_entity.x) == 0 and round(proto_entity.y) == 0 and \
            proto_entity.name != common.SUN or \
                proto_entity.name == common.OCESS:
            del proto_state.entities[entity_index]
        else:
            entity_index += 1

    hab.artificial = True
    ayse.artificial = True
    # Habitat and AYSE masses are hardcoded in OrbitV.
    hab.mass = 275000
    ayse.mass = 20000000

    orbitx_state = state.PhysicsState(None, proto_state)
    orbitx_state[common.HABITAT] = state.Entity(hab)
    orbitx_state[common.AYSE] = state.Entity(ayse)

    craft = orbitx_state.craft_entity()
    craft.throttle = craft_throttle
    orbitx_state[orbitx_state.craft] = craft

    log.debug(f'Interpreted {rnd_path} and {starsr_path} into this state:')
    log.debug(repr(orbitx_state))
    orbitx_state = _separate_landed_entities(orbitx_state)
    return orbitx_state


def read_update_from_orbitsse(orbitsse_path: Path) -> network.Request:
    """Reads information from ORBITSSE.RND and returns an ENGINEERING_UPDATE
    that contains the information."""
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


def _read_long(file) -> int:
    return int.from_bytes(file.read(4), byteorder='little')


def _read_single(file) -> float:
    return struct.unpack("<f", file.read(4))[0]


def _read_double(file) -> float:
    return struct.unpack("<d", file.read(8))[0]


def _string_to_float(item: str) -> float:
    return float(item.upper().replace('#', '').replace('D', 'E'))


def _separate_landed_entities(orbitx_state: state.PhysicsState) \
        -> state.PhysicsState:
    n = len(orbitx_state)
    # 2xN of (x, y) positions
    posns = numpy.column_stack((orbitx_state.X, orbitx_state.Y))
    # An n*n matrix of _altitudes_ between each entity
    radii = numpy.array([entity.r for entity in orbitx_state])
    alt_matrix = (
        scipy.spatial.distance.cdist(posns, posns) -
        numpy.array([radii]) - numpy.array([radii]).T)
    numpy.fill_diagonal(alt_matrix, numpy.inf)

    # Find everything that has a very small or negative altitude, and make
    # sure that it has an altitude of at least 1.
    infinite_loop_warning = 0
    while numpy.min(alt_matrix) < 1:
        infinite_loop_warning += 1
        assert infinite_loop_warning <= len(orbitx_state)

        flattened_index = alt_matrix.argmin()
        e1_index = flattened_index // n
        e2_index = flattened_index % n
        e1 = orbitx_state[e1_index]
        e2 = orbitx_state[e2_index]
        alt = numpy.min(alt_matrix)
        assert abs(numpy.min(alt_matrix)) < 10, (
            f"{e1.name} and {e2.name} were loaded from the OrbitV savefile, "
            "but they greatly intersect each other with "
            f"altitude={alt}. This probably shouldn't happen!")

        if e1.mass < e2.mass:
            smaller = e1
            larger = e2
        else:
            smaller = e2
            larger = e1

        norm = smaller.pos - larger.pos
        norm = norm / numpy.linalg.norm(norm)

        smaller.pos += norm * (alt + 1)
        orbitx_state[smaller.name] = smaller

        posns = numpy.column_stack((orbitx_state.X, orbitx_state.Y))
        alt_matrix = (
            scipy.spatial.distance.cdist(posns, posns) -
            numpy.array([radii]) - numpy.array([radii]).T)
        numpy.fill_diagonal(alt_matrix, numpy.inf)

    return orbitx_state
