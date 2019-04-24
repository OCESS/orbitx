from typing import List

import numpy as np
import vpython

from orbitx import calc
from orbitx import common
from orbitx.graphics.flight_gui import FlightGui


class OrbitProjection:
    """A projection of the orbit of the active ship around the reference."""

    def __init__(self, flight_gui: FlightGui):
        self._flight_gui = flight_gui
        self._projection = vpython.ring(
            axis=vpython.vector(0, 0, 1), opacity=0)

    def update(self):
        orb_params = calc.orbit_parameters(
            self._flight_gui.reference(), self._flight_gui.active_craft())
        pos = orb_params.centre - self._flight_gui.origin().pos
        self._projection.pos = vpython.vector(pos[0], pos[1], 0)
        # size.x is actually the thickness, confusingly.
        self._projection.size.x = min(
            common.PROJECTION_THICKNESS * self._flight_gui._scene.range,
            0.1 * max(orb_params.major_axis, orb_params.minor_axis))
        # size.y and size.z are the width and length of the ellipse.
        self._projection.size.y = orb_params.major_axis
        self._projection.size.z = orb_params.minor_axis
        self._projection.rotate(angle=-orb_params.orientation - np.arctan2(
            self._projection.up.y, self._projection.up.x)
        )

    def show(self, visible: bool):
        self._projection.opacity = int(visible)


def hypoerbolic_orbit(orb_params: calc.OrbitCoords) -> List[calc.Point]:
    pass
