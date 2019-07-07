import logging
from abc import ABCMeta
from abc import abstractmethod
from pathlib import Path
from typing import Optional, Union

import vpython
import numpy as np

from orbitx import calc
from orbitx import common
from orbitx import state

log = logging.getLogger()


class ThreeDeeObj(metaclass=ABCMeta):

    @abstractmethod
    def _create_obj(self,
                    entity: state.Entity, origin: state.Entity,
                    texture: Optional[str]
                    ) -> Union[vpython.sphere, vpython.compound]:
        """Create a 3D object, like a planet, a star, or a spaceship, using
        vpython and return it. It will be rotated etc. elsewhere, don't worry
        about that. Just make a cool object!"""
        pass

    @abstractmethod
    def _label_text(self, entity: state.Entity) -> str:
        """Return text that should be put in the label for a 3d object.
        This method is evaluated every frame using the newest physics data."""
        pass

    # When creating a new 3D object, usually you don't have to worry about
    # anything below here. All you have to do is override the three above
    # methods in your derived class.
    # Sometimes you'll want to do something special, e.g. AYSE disables
    # landing graphics being drawn by overriding draw_landing_graphic below
    # to be a no-op, which you can do. But most of the time, it's not needed.

    LANDING_GRAPHIC_OPAQUE_ALTITUDE = 100_000
    LANDING_GRAPHIC_TRANSPARENT_ALTITUDE = 750_000

    def __init__(self, entity: state.Entity,
                 origin: state.Entity, texture_path: Path) -> None:
        texture_path = texture_path / (entity.name + '.jpg')

        texture = str(texture_path) if texture_path.is_file() else None
        self._obj = self._create_obj(entity, origin, texture)
        assert self._obj is not None

        self._small_landing_graphic: Optional[vpython.compound] = None
        self._large_landing_graphic: Optional[vpython.compound] = None
        self._label = vpython.label(
            pos=self._obj.pos, xoffset=10, yoffset=10, border=4, font='sans',
            text=self._label_text(entity))

    def draw_landing_graphic(self, entity: state.Entity) -> None:
        log.debug(f'drawing landing graphic for {entity.name}')
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
                           if entity.name == common.EARTH else
                           vpython.vector(0.5, 0.5, 0.5)))
                    for coord in tri]
                vpython_tris.append(vpython.triangle(vs=vpython_verts))
            return vpython.compound(
                vpython_tris,
                opacity=0,
                pos=self._obj.pos,
                up=vpython.vector(0, 0, 1))

        # We have to have to sizes because we want our landing graphic to be
        # visible at large zoom levels (the large one won't be, because vpython
        # is weird like that), but also show a seamless transition to the
        # planet (the small one will look like a line from a top-down view)
        self._small_landing_graphic = graphic(5000)
        self._large_landing_graphic = graphic(
            entity.r * np.tan(np.degrees(30)))

    def _update_landing_graphic(
        self, graphic: vpython.compound,
        entity: state.Entity, craft: state.Entity
    ) -> None:
        """Rotate the landing graphic to always be facing the Habitat.

        The landing graphic has to be on the surface of the planet,
        but also the part of the planet closest to the habitat."""
        if graphic is None:
            # We haven't drawn a landing graphic yet.
            return

        axis = vpython.vector(
            craft.x - entity.x,
            craft.y - entity.y,
            0
        )

        graphic.axis = vpython.vector(-axis.y, axis.x, 0).norm()
        graphic.pos = (
            self._obj.pos + axis.norm() * (entity.r - graphic.width / 2)
        )

        # Make the graphic transparent when far, but opaque when close.
        # This is a y = mx + b line, clamped to [0, 1]
        slope = 1 / (self.LANDING_GRAPHIC_OPAQUE_ALTITUDE -
                     self.LANDING_GRAPHIC_TRANSPARENT_ALTITUDE)
        y_intercept = -slope * self.LANDING_GRAPHIC_TRANSPARENT_ALTITUDE
        opacity = slope * (axis.mag - entity.r) + y_intercept
        graphic.opacity = max(0, min(opacity, 1))

    def _show_hide_label(self) -> None:
        self._label.visible = not self._label.visible

    def _update_obj(self, entity: state.Entity,
                    state: state.PhysicsState, origin: state.Entity) -> None:
        # update planet objects
        self._obj.pos = entity.screen_pos(origin)
        self._obj.axis = calc.angle_to_vpy(entity.heading)

        # update label objects
        self._label.text = self._label_text(entity)
        self._label.pos = entity.screen_pos(origin)
        # update landing graphic objects
        self._update_landing_graphic(self._small_landing_graphic,
                                     entity, state.craft_entity())
        self._update_landing_graphic(self._large_landing_graphic,
                                     entity, state.craft_entity())

    def pos(self) -> vpython.vector:
        return self._obj.pos

    def relevant_range(self) -> float:
        return self._obj.radius * 2

    def draw(self, entity: state.Entity,
             state: state.PhysicsState, origin: state.Entity):
        self._update_obj(entity, state, origin)

    def clear_trail(self) -> None:
        self._obj.clear_trail()

    def make_trail(self, trails: bool) -> None:
        self.clear_trail()
        self._obj.make_trail = trails
