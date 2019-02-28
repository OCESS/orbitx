from . import common
from enum import Enum
from typing import List
import vpython
from . import orbitx_pb2 as protos  # physics module
import numpy as np
import math


ORIGIN = 0
REFERENCE = 1
TARGET = 2
HABITAT = 3

G = 6.674e-11
ORT = [None, None, None, None]  # ORT consists of origin, reference and target.
#vpython = vp.vp()


def set_ORT(origin: protos.Entity, reference: protos.Entity,
            target: protos.Entity, ahabitat: protos.Entity):
    ORT[ORIGIN] = origin
    ORT[REFERENCE] = reference
    ORT[TARGET] = target
    ORT[HABITAT] = ahabitat
# end of set_ORT


def origin() -> protos.Entity:
    return ORT[ORIGIN]
# end of origin


def reference() -> protos.Entity:
    return ORT[REFERENCE]
# end of reference


def target() -> protos.Entity:
    return ORT[TARGET]
# end of target


def habitat() -> protos.Entity:
    return ORT[HABITAT]
# end of habitat


def physicalSate() -> protos.PhysicalState:
    return ORT[PHYSICALSTATE]
# end of physicalSate


def posn(entity: protos.Entity) -> vpython.cyvector.vector:
    """ posn returns a vector object that its value represents translates into 
        the frame of reference of the origin.
    """
    return vpython.vector(
        entity.x - origin().x,
        entity.y - origin().y,
        0)
# end of posn


def ang_pos(angle: float) -> vpython.cyvector.vector:
    return vpython.vector(np.cos(angle), np.sin(angle), 0)
# end of _ang_pos


def orb_speed(reference: protos.Entity) -> float:
    """The orbital speed of an astronomical body or object.
    Equation referenced from https://en.wikipedia.org/wiki/Orbital_speed"""
    return vpython.sqrt((G * reference.mass) / reference.r)
# end of _orb_speed


def periapsis(habitat: protos.Entity) -> float:
    # reference = reference()
    # calculate and return the periapsis
    return 100
# end of _periapsis


def apoapsis(habitat: str) -> float:
    # reference = reference()
    # calculate and return the apoapsis
    return 100
# end of _apoapsis


def altitude(planet1: protos.Entity, planet2: protos.Entity) -> float:
    """Caculate distance between ref_planet and Habitat
    returns: the number of metres"""

    return math.hypot(
        planet1.x - planet2.x,
        planet1.y - planet2.y
    ) - planet1.r - planet2.r
# end of _altitude


def speed(planet1: protos.Entity, planet2: protos.Entity) -> float:
    """Caculate speed between ref_planet and Habitat"""
    return vpython.mag(vpython.vector(
        planet1.vx - planet2.vx,
        planet1.vy - planet2.vy,
        0
    ))
# end of _speed


def v_speed(planet1: protos.Entity, planet2: protos.Entity) -> float:
    """Centripetal velocity of the habitat relative to planet_name.

    Returns a negative number of m/s when the habitat is falling,
    and positive when the habitat is rising."""
    return 100
# end of _v_speed


def h_speed(planet1: protos.Entity, planet2: protos.Entity) -> float:
    """Tangential velocity of the habitat relative to planet_name.

    Always returns a positive number of m/s, of how fast the habitat is
    moving side-to-side relative to the reference surface."""
    return 100
# end of _h_speed


def unit_velocity(entity: protos.Entity) -> vpython.cyvector.vector:
    """Provides entity velocity relative to reference."""
    return vpython.vector(
        entity.vx - reference().vx,
        entity.vy - reference().vy,
        0).norm()
# end of _unit_velocity
