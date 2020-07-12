# TODO: explain

from typing import Optional

import vpython

import orbitx.common as common
from orbitx.graphics.planet import Planet
from orbitx.graphics.threedeeobj import ThreeDeeObj


class LandingGraphic:

    def __init__(self):
        self._landing_graphic = vpython.extrusion(
                path=[vpython.vec(0, 0, 0), vpython.vec(1, 0, 0)],
                shape=vpython.shapes.circle(radius=1),
                up=common.DEFAULT_UP,
                forward=common.DEFAULT_FORWARD
            )
        self._attached_3dobj: Optional[ThreeDeeObj] = None

    def draw(self, obj: ThreeDeeObj) -> None:
        """Draw something that simulates a flat surface at near zoom levels."""
        self._attached_3dobj = obj
        if isinstance(obj, Planet):
            self._landing_graphic.size = (
                obj._obj.radius * vpython.vector(0.1, 1, 1)
            )
            self._landing_graphic.texture = obj._obj.texture
        else:
            print("BARP")

    def update(self, craft: ThreeDeeObj, map_mode: bool) -> None:
        """Rotate the landing graphic to always be facing the Habitat.

        The landing graphic has to be on the surface of the planet,
        but also the part of the planet closest to the habitat."""
        if self._landing_graphic is None:
            # We haven't drawn a landing graphic yet.
            return
        if map_mode:
            # Don't draw the landing graphic in map mode.
            self._landing_graphic.visible = False
            return
        else:
            self._landing_graphic.visible = True

        self._landing_graphic.axis = (
            craft._obj.pos - self._attached_3dobj._obj.pos
        ).norm()

        self._landing_graphic.pos = (
                self._attached_3dobj._obj.pos
                + self._landing_graphic.axis
                * (self._attached_3dobj._obj.radius - self._landing_graphic.length / 2 - 1)
        )
