from typing import List, Tuple
import vpython
from . import orbitx_pb2 as protos  # physics module
import numpy as np
import math
import collections


ORIGIN = 0
REFERENCE = 1
TARGET = 2
HABITAT = 3

G = 6.674e-11
ORT: List[protos.Entity] = [None, None, None, None]
Point = collections.namedtuple('Point', ['x', 'y', 'z'])


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


def posn(entity: protos.Entity) -> vpython.vector:
    """ posn returns a vector object that its value represents translates into
        the frame of reference of the origin.
    """
    return vpython.vector(
        entity.x - origin().x,
        entity.y - origin().y,
        0)
# end of posn


def ang_pos(angle: float) -> vpython.vector:
    return vpython.vector(np.cos(angle), np.sin(angle), 0)
# end of _ang_pos


def phase_angle() -> float:
    """The orbital phase angle, habitat-reference-target.
    i.e. the angle between the ref-hab vector and the ref-targ vector."""
    # Code from Newton Excel Bach blog, 2014, "the angle between two vectors"
    ref_pos = np.array([reference().x, reference().y])
    hab_relative = np.array([habitat().x, habitat().y]) - ref_pos
    targ_relative = np.array([target().x, target().y]) - ref_pos
    return np.degrees(
        np.arctan2(hab_relative[1], hab_relative[0]) -
        np.arctan2(targ_relative[1], targ_relative[0])
    ) % 360


def orb_speed(reference: protos.Entity) -> float:
    """The orbital speed of an astronomical body or object.
    Equation referenced from https://en.wikipedia.org/wiki/Orbital_speed"""
    return np.sqrt(
        (reference.mass**2 * G) /
        ((habitat().mass + reference.mass) * distance(reference, habitat())))
# end of _orb_speed


def altitude(planet1: protos.Entity, planet2: protos.Entity) -> float:
    """Caculate distance between ref_planet and Habitat
    returns: the number of metres"""

    return distance(planet1, planet2) - planet1.r - planet2.r
# end of _altitude


def distance(planet1: protos.Entity, planet2: protos.Entity) -> float:
    return math.hypot(planet1.x - planet2.x, planet1.y - planet2.y)


def speed(planet1: protos.Entity, planet2: protos.Entity) -> float:
    """Caculate speed between ref_planet and Habitat"""
    return vpython.mag(vpython.vector(
        planet1.vx - planet2.vx,
        planet1.vy - planet2.vy,
        0
    ))
# end of _speed


def v_speed(entityA: protos.Entity, entityB: protos.Entity) -> float:
    """Centripetal velocity of the habitat relative to planet_name.

    Returns a negative number of m/s when the habitat is falling,
    and positive when the habitat is rising."""
    v = np.array([entityA.vx - entityB.vx, entityA.vy - entityB.vy])
    normal = np.array([entityA.x - entityB.x, entityA.y - entityB.y])
    normal = normal / np.linalg.norm(normal)
    radial_v = np.dot(normal, v)
    return np.linalg.norm(radial_v)
# end of _v_speed


def h_speed(entityA: protos.Entity, entityB: protos.Entity) -> float:
    """Tangential velocity of the habitat relative to planet_name.

    Always returns a positive number of m/s, of how fast the habitat is
    moving side-to-side relative to the reference surface."""
    v = np.array([entityA.vx - entityB.vx, entityA.vy - entityB.vy])
    normal = np.array([entityA.x - entityB.x, entityA.y - entityB.y])
    normal = normal / np.linalg.norm(normal)
    tangent = np.array([normal[1], -normal[0]])
    tangent_v = np.dot(tangent, v)
    return np.linalg.norm(tangent_v)
# end of _h_speed


def unit_velocity(entity: protos.Entity) -> vpython.vector:
    """Provides entity velocity relative to reference."""
    return vpython.vector(
        entity.vx - reference().vx,
        entity.vy - reference().vy,
        0).norm()
# end of _unit_velocity


def pitch(entity: protos.Entity) -> vpython.vector:
    """....."""
    return np.degrees(entity.heading)
# end of pitch


def landing_acceleration(
        planet1: protos.Entity, planet2: protos.Entity) -> vpython.vector:
    """....."""
    return 100
# end of landing_acceleration


def semimajor_axis(entityA: protos.Entity, entityB: protos.Entity) -> float:
    """Calculate semimajor axis: the mean distance between bodies in an
    elliptical orbit. See 'calculation of semi-major axis from state vectors'
    on the wikipedia article for semi-major axes."""
    v = np.array([entityA.vx - entityB.vx, entityA.vy - entityB.vy])
    r = distance(entityA, entityB)
    mu = (entityB.mass + entityA.mass) * G
    E = np.dot(v, v) / 2 - mu / r
    return -mu / (2 * E)


def eccentricity(entityA: protos.Entity, entityB: protos.Entity) -> float:
    """Calculates the eccentricity - a defining feature of ellipses.
    See https://en.wikipedia.org/wiki/Orbital_eccentricity for the equation."""
    v = np.array([entityA.vx - entityB.vx, entityA.vy - entityB.vy])
    r = np.array([entityA.x - entityB.x, entityA.y - entityB.y])
    mu = (entityB.mass + entityA.mass) * G  # G(m + M)
    E = np.dot(v, v) / 2 - mu / np.linalg.norm(r)  # v^2/2 - mu/dist
    h = np.cross(r, v)  # r (cross) v
    return np.sqrt(1 + (2 * E * np.dot(h, h)) / (mu**2))


def periapsis(entityA: protos.Entity, entityB: protos.Entity) -> float:
    """Calculates the lowest altitude in the orbit of entityA above entityB.

    A negative means at some point in entityA's orbit, entityA will crash into
    the surface of entityB."""
    peri_distance = (
        semimajor_axis(entityA, entityB) *
        (1 - eccentricity(entityA, entityB))
    )
    return max(peri_distance - entityB.r, 0)


def apoapsis(entityA: protos.Entity, entityB: protos.Entity) -> float:
    """Calculates the highest altitude in the orbit of entityA above entityB.

    A positive apoapsis means at some point in entityA's orbit, entityA will
    be above the surface of entityB."""
    apo_distance = (
        semimajor_axis(entityA, entityB) *
        (1 + eccentricity(entityA, entityB))
    )
    return max(apo_distance - entityB.r, 0)


def midpoint(left: np.ndarray, right: np.ndarray, radius: float) -> np.ndarray:
    # Find the midpoint between the xyz-tuples left and right, but also
    # on the surface of a sphere (so not just a simple average).
    midpoint = (left + right) / 2
    midpoint_radial_dist = np.linalg.norm(midpoint)
    return radius * midpoint / midpoint_radial_dist
# end of midpoint


def _build_sphere_segment_vertices(
        radius: float,
        size: float,
        refine_steps=3) -> List[Tuple[Point, Point, Point]]:
    """Returns a segment of a sphere, which has a specified radius.
    The return is a list of xyz-tuples, each representing a vertex."""
    # This code inspired by:
    # http://blog.andreaskahler.com/2009/06/creating-icosphere-mesh-in-code.html
    # Thanks, Andreas Kahler.
    # TODO: limit the number of vertices generated to 65536 (the max in a
    # vpython compound object).

    # We set the 'middle' of the surface we're constructing
    # to be (0, 0, r). Think of this as a point on the surface of
    # the sphere centred on (0,0,0) with radius r.
    # Then, we construct four equilateral triangles that will all meet at
    # this point. Each triangle is `size` metres long.

    # The values of 100 are placeholders,
    # and get replaced by cos(theta) * r
    tris = np.array([
        (Point(0, 1, 100), Point(1, 0, 100), Point(0, 0, 100)),
        (Point(1, 0, 100), Point(0, -1, 100), Point(0, 0, 100)),
        (Point(0, -1, 100), Point(-1, 0, 100), Point(0, 0, 100)),
        (Point(-1, 0, 100), Point(0, 1, 100), Point(0, 0, 100))
    ])
    # Each Point gets coerced to a length-3 numpy array

    # Set the z of each xyz-tuple to be radius, and everything else to be
    # the coordinates on the radius-sphere times -1, 0, or 1.
    theta = np.arctan(size / radius)
    tris = np.where(
        [True, True, False],
        radius * np.sin(theta) * tris,
        radius * np.cos(theta))

    for _ in range(0, refine_steps):
        new_tris = np.ndarray(shape=(0, 3, 3))
        for tri in tris:
            # A tri is a 3-tuple of xyz-tuples.
            a = midpoint(tri[0], tri[1], radius)
            b = midpoint(tri[1], tri[2], radius)
            c = midpoint(tri[2], tri[0], radius)

            # Turn one triangle into a triforce projected onto a sphere.
            new_tris = np.append(new_tris, [
                (tri[0], a, c),
                (tri[1], b, a),
                (tri[2], c, b),
                (a, b, c)  # The centre triangle of the triforce
            ], axis=0)
        tris = new_tris

    return tris
# end of _build_sphere_segment_vertices
