import math
from typing import List

import vpython

from orbitx import calc
from orbitx import state


class OrbitProjection:
    """A projection of the orbit of the active ship around the reference."""
    POINTS_IN_HYPERBOLA = 500
    HYPERBOLA_RADIUS = 1e2

    # Thickness of orbit projections, scaled to how zoomed-out the viewport is.
    PROJECTION_THICKNESS = 0.005

    def __init__(self):
        self._visible = False

        # There are two cases that we care about for a 2-body orbit, elliptical
        # or hyperbolic. Make a graphic for either case.
        self._ring = vpython.ring(
            axis=vpython.vector(0, 0, 1), visible=False)

        # Since vpython doesn't have a hyperbola primitive, we make one ourself
        # by generating a bunch of points along a hyperbola. Look at this graph
        # https://www.desmos.com/calculator/dbhsftzyjc
        # or put the following into wolframalpha.com
        # parametric graph sinh(t), cosh(t) from t = -asinh(1e2) to asinh(1e2)
        hyperbola_points: List[vpython.vector] = []
        start_t = -math.asinh(self.POINTS_IN_HYPERBOLA)
        for i in range(0, self.POINTS_IN_HYPERBOLA + 1):
            t = start_t + abs(start_t) * 2 * i / self.POINTS_IN_HYPERBOLA
            hyperbola_points.append(vpython.vector(
                math.sinh(t), math.cosh(t), 0))

        self._hyperbola = vpython.curve(
            hyperbola_points, axis=vpython.vector(1, 1, 0), up=vpython.vec(-1, 0, 0))
        self._hyperbola.visible = False

    def update(self, state: state.PhysicsState, origin: state.Entity):
        if not self._visible:
            self._hyperbola.visible = False
            self._ring.visible = False
            return

        orb_params = calc.orbit_parameters(
            state.reference_entity(), state.craft_entity())
        thickness = min(
            self.PROJECTION_THICKNESS * vpython.canvas.get_selected().range,
            abs(0.1 * max(orb_params.major_axis, orb_params.minor_axis))
        )
        pos = orb_params.centre - origin.pos
        direction = vpython.vector(*orb_params.eccentricity, 0)
        e_mag = calc.fastnorm(*orb_params.eccentricity)

        if e_mag < 1:
            # Project an elliptical orbit
            self._hyperbola.visible = False
            self._ring.pos = vpython.vector(*pos, 0)
            # size.x is actually the thickness, confusingly.
            # size.y and size.z are the width and length of the ellipse.
            self._ring.size.y = orb_params.major_axis
            self._ring.size.z = orb_params.minor_axis
            self._ring.up = direction
            self._ring.size.x = thickness
            self._ring.visible = True

        elif e_mag > 1:
            # Project a hyperbolic orbit
            self._ring.visible = False
            self._hyperbola.origin = vpython.vector(*pos, 0)

            # For a vpython.curve object, setting the axis is confusing.
            # To control direction, set the .up attribute (magnitude doesn't
            # matter for .up)
            # To control size, set the .size attribute (magnitude matters).
            # Setting .axis will also change .size, not sure how.

            self._hyperbola.size = vpython.vector(
                orb_params.minor_axis / 2, orb_params.major_axis / 2, 1)
            self._hyperbola.up = -direction
            self._hyperbola.radius = thickness
            self._hyperbola.visible = True
            assert self._hyperbola.axis.z == 0, self._hyperbola.axis
            assert self._hyperbola.up.z == 0, self._hyperbola.up

        else:
            # e == 1 pretty much never happens, and if it does we'll just wait
            # until it goes away
            return

    def show(self, visible: bool):
        self._visible = visible
