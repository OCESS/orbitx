import logging
from abc import ABCMeta
from abc import abstractmethod
from pathlib import Path
from typing import Optional

import vpython
import numpy as np

import orbitx.calculator
import orbitx.calculator as calc
import orbitx.state as state
import numpy as np
import math

log = logging.getLogger()


class Displayable(metaclass=ABCMeta):
    PLANET_SHININIESS = 0.3
    LANDING_GRAPHIC_OPAQUE_ALTITUDE = 100_000
    LANDING_GRAPHIC_TRANSPARENT_ALTITUDE = 750_000

    def __init__(self, entity: state.Entity, texture_path: Path) -> None:
        self._obj: vpython.sphere
        self._label: vpython.label
        self._small_landing_graphic: vpython.compound
        self._texture: Optional[str]

        self._entity = entity

        texture = texture_path / (self._entity.name + '.jpg')
        self._texture = str(texture) if texture.is_file() else None
        self._small_landing_graphic: Optional[vpython.compound] = None
        self._large_landing_graphic: Optional[vpython.compound] = None
    # end of __init__

    def _create_label(self) -> vpython.label:
        return vpython.label(
            visible=True, pos=calc.posn(self._entity),
            xoffset=0, yoffset=10, height=16,
            border=4, font='sans')

    def draw_landing_graphic(self, entity: state.Entity) -> None:
        """Draw something that simulates a flat surface at near zoom levels."""
        def graphic(size: float):
            # Iterate over a list of Point 3-tuples, each representing the
            # vertices of a triangle in the sphere segment.
            vpython_tris = []
            for tri in calc._build_sphere_segment_vertices(entity.r, size):
                # TODO: we pick an ocean blue colour for Earth, but really we
                # should find a better way to make the landing graphic not a
                # hardcoded value after the demo.
                vpython_verts = [vpython.vertex(
                    pos=vpython.vector(*coord),
                    color=(vpython.vector(0, 0.6, 0.8)
                           if entity.name == 'Earth' else
                           vpython.vector(0.5, 0.5, 0.5)))
                    for coord in tri]
                vpython_tris.append(vpython.triangle(vs=vpython_verts))
            return vpython.compound(
                vpython_tris,
                pos=calc.posn(entity), up=vpython.vector(0, 0, 1))

        # We have to have to sizes because we want our landing graphic to be
        # visible at large zoom levels (the large one won't be, because vpython
        # is weird like that), but also show a seamless transition to the
        # planet (the small one will look like a line from a top-down view)
        self._small_landing_graphic = graphic(5000)
        self._large_landing_graphic = graphic(
            entity.r * np.tan(np.degrees(30)))
    # end of draw_small_landing_graphic

    def _update_landing_graphic(
        self, graphic: vpython.compound, entity: state.Entity
    ) -> None:
        """Rotate the landing graphic to always be facing the Habitat.

        The landing graphic has to be on the surface of the planet,
        but also the part of the planet closest to the habitat."""
        if graphic is None:
            # We haven't drawn a landing graphic yet.
            return

        axis = vpython.vector(
            calc.habitat().x - entity.x,
            calc.habitat().y - entity.y,
            0
        )

        graphic.axis = vpython.vector(-axis.y, axis.x, 0).norm()
        graphic.pos = (
            calc.posn(entity) +
            axis.norm() * (entity.r - graphic.width / 2)
        )

        # Make the graphic transparent when far, but opaque when close.
        # This is a y = mx + b line, clamped to [0, 1]
        slope = 1 / (self.LANDING_GRAPHIC_OPAQUE_ALTITUDE -
                     self.LANDING_GRAPHIC_TRANSPARENT_ALTITUDE)
        y_intercept = -slope * self.LANDING_GRAPHIC_TRANSPARENT_ALTITUDE
        opacity = slope * (axis.mag - entity.r) + y_intercept
        graphic.opacity = max(0, min(opacity, 1))
    # end of _update_small_landing_graphic

    def _show_hide_label(self) -> None:
        self._label.visible = not self._label.visible

    def _update_obj(self, entity: state.Entity) -> None:
        self._entity = entity
        # update planet objects
        self._obj.pos = calc.posn(self._entity)
        if entity.name == "AYSE":
            self._obj.axis = calc.ang_pos(self._entity.heading + np.pi)
        else:
            self._obj.axis = calc.ang_pos(self._entity.heading)

        # update label objects
        self._label.text = self._label.text_function(entity)
        self._label.pos = calc.posn(entity)
        # update landing graphic objects
        self._update_landing_graphic(self._small_landing_graphic, entity)
        self._update_landing_graphic(self._large_landing_graphic, entity)
    # end of _update_obj

    def get_obj(self):  # -> (any of vpython.sphere, vpython.compound)
        return self._obj
    # end of get_obj

    def relevant_range(self) -> float:
        return self._obj.radius * 2
    # end of relevant_range

    @abstractmethod
    def _draw_labels(self) -> None:
        pass
    # end of _draw_labels

    @abstractmethod
    def draw(self, entity: state.Entity) -> None:
        pass
    # end of draw

    @abstractmethod
    def clear_trail(self) -> None:
        pass

    @abstractmethod
    def trail_option(self, stop: bool = False) -> None:
        pass
# end of class Displayable
