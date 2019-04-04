from typing import List, Tuple
import collections

import vpython
import numpy as np

import orbitx.state as state

G = 6.674e-11
Point = collections.namedtuple('Point', ['x', 'y', 'z'])


def angle_to_vpy(angle: float) -> vpython.vector:
    return vpython.vector(np.cos(angle), np.sin(angle), 0)


def phase_angle(A: state.Entity, B: state.Entity, C: state.Entity) -> float:
    """The orbital phase angle, between A-B-C, of the angle at B.
    i.e. the angle between the ref-hab vector and the ref-targ vector."""
    # Code from Newton Excel Bach blog, 2014, "the angle between two vectors"
    AB = A.pos - B.pos
    CB = C.pos - B.pos

    return np.degrees(
        np.arctan2(AB[1], AB[0]) -
        np.arctan2(CB[1], CB[0])
    ) % 360


def orb_speed(habitat: state.Entity, reference: state.Entity) -> float:
    """The orbital speed of an astronomical body or object.
    Equation referenced from https://en.wikipedia.org/wiki/Orbital_speed"""
    return np.sqrt(
        (reference.mass**2 * G) /
        ((habitat.mass + reference.mass) *
         distance(reference, habitat)))


def altitude(A: state.Entity, B: state.Entity) -> float:
    """Caculate distance between ref_planet and Habitat
    returns: the number of metres"""
    return distance(A, B) - A.r - B.r


def distance(A: state.Entity, B: state.Entity) -> float:
    return np.linalg.norm(A.pos - B.pos)


def speed(A: state.Entity, B: state.Entity) -> float:
    """Caculate speed between ref_planet and Habitat"""
    return np.linalg.norm(A.v - B.v)


def v_speed(A: state.Entity, B: state.Entity) -> float:
    """Centripetal velocity of the habitat relative to planet_name.

    Returns a negative number of m/s when the habitat is falling,
    and positive when the habitat is rising."""
    v = A.v - B.v
    normal = A.pos - B.pos
    normal = normal / np.linalg.norm(normal)
    radial_v = np.dot(normal, A.v - B.v)
    return np.linalg.norm(radial_v)


def h_speed(A: state.Entity, B: state.Entity) -> float:
    """Tangential velocity of the habitat relative to planet_name.

    Always returns a positive number of m/s, of how fast the habitat is
    moving side-to-side relative to the reference surface."""
    normal = A.pos - B.pos
    normal = normal / np.linalg.norm(normal)
    tangent = np.array([normal[1], -normal[0]])
    tangent_v = np.dot(tangent, A.v - B.v)
    return np.linalg.norm(tangent_v)


def pitch(entity: state.Entity) -> float:
    """....."""
    return np.degrees(entity.heading)


def landing_acceleration(A: state.Entity, B: state.Entity) -> float:
    """....."""
    return 100


def semimajor_axis(A: state.Entity, B: state.Entity) -> float:
    """Calculate semimajor axis: the mean distance between bodies in an
    elliptical orbit. See 'calculation of semi-major axis from state vectors'
    on the wikipedia article for semi-major axes."""
    v = np.array([A.vx - B.vx, A.vy - B.vy])
    r = distance(A, B)
    mu = (B.mass + A.mass) * G
    E = np.dot(v, v) / 2 - mu / r
    return -mu / (2 * E)


def eccentricity(A: state.Entity, B: state.Entity) -> float:
    """Calculates the eccentricity - a defining feature of ellipses.
    See https://en.wikipedia.org/wiki/Orbital_eccentricity for the equation."""
    v = A.v - B.v
    mu = (B.mass + A.mass) * G  # G(m + M)
    E = np.dot(v, v) / 2 - mu / distance(A, B)  # v^2/2 - mu/dist
    h = np.cross(A.pos - B.pos, v)  # r (cross) v
    return np.sqrt(1 + (2 * E * np.dot(h, h)) / (mu**2))


def periapsis(A: state.Entity, B: state.Entity) -> float:
    """Calculates the lowest altitude in the orbit of A above B.

    A negative means at some point in A's orbit, A will crash into
    the surface of B."""
    peri_distance = (
        semimajor_axis(A, B) *
        (1 - eccentricity(A, B))
    )
    return max(peri_distance - B.r, 0)


def apoapsis(A: state.Entity, B: state.Entity) -> float:
    """Calculates the highest altitude in the orbit of A above B.

    A positive apoapsis means at some point in A's orbit, A will
    be above the surface of B."""
    apo_distance = (
        semimajor_axis(A, B) *
        (1 + eccentricity(A, B))
    )
    return max(apo_distance - B.r, 0)


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
