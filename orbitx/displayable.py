from abc import ABCMeta
from abc import abstractmethod
from pathlib import Path
import vpython
import logging
from . import orbitx_pb2 as protos  # physics module
import orbitx.calculator
import orbitx.calculator as calc
import numpy as np
import math

log = logging.getLogger()


class Displayable(metaclass=ABCMeta):
    PLANET_SHININIESS = 0.3
    _target_landing_graphic: vpython.compound = None
    _reference_landing_graphic: vpython.compound = None

    @staticmethod
    def _draw_landing_graphic(entity: protos.Entity) -> vpython.compound:
        """Draw something that simulates a flat surface at near zoom levels.

        Only draws the landing graphic on the target and reference."""
        # Iterate over a list of Point 3-tuples, each representing the
        # vertices of a triangle in the sphere segment.
        vpython_tris = []
        for tri in calc._build_sphere_segment_vertices(entity.r):
            vpython_verts = [vpython.vertex(pos=vpython.vector(*coord))
                             for coord in tri]
            vpython_tris.append(vpython.triangle(vs=vpython_verts))
        return vpython.compound(
            vpython_tris, pos=calc.posn(entity), up=vpython.vector(0, 0, 1))
    # end of _draw_landing_graphic

    @staticmethod
    def _update_landing_graphic(entity: protos.Entity,
                                landing_graphic: vpython.compound) -> None:
        """Rotate the landing graphic to always be facing the Habitat.

        The landing graphic has to be on the surface of the planet,
        but also the part of the planet closest to the habitat."""
        axis = vpython.vector(
            calc.habitat().x - entity.x,
            calc.habitat().y - entity.y,
            0
        ).norm()

        landing_graphic.axis = vpython.vector(axis.y, -axis.x, 0)
        landing_graphic.pos = (
            calc.posn(entity) + axis * (entity.r - landing_graphic.width / 2)
        )
    # end of _update_landing_graphic

    def __init__(self, entity: protos.Entity, texture_path: Path) -> None:
        self._entity = entity
        self._obj = None
        self._label = None
        self._texture: str

        texture = texture_path / (self._entity.name + '.jpg')
        self._texture = str(texture) if texture.is_file() else None
        self._landing_graphic: vpython.compound = None
    # end of __init__

    def _create_label(self) -> vpython.label:
        return vpython.label(
            visible=True, pos=calc.posn(self._entity),
            xoffset=0, yoffset=10, height=16,
            border=4, font='sans')

    def _show_hide_label(self) -> None:
        self._label.visible = not self._label.visible

    def _update_obj(self, entity: protos.Entity) -> None:
        self._entity = entity
        # update planet objects
        self._obj.pos = calc.posn(self._entity)
        if entity.name == "AYSE":
            self._obj.axis = calc.ang_pos(self._entity.heading+np.pi)
        else:
            self._obj.axis = calc.ang_pos(self._entity.heading)
        # update label objects
        self._label.text = self._label.text_function(self._entity)
        self._label.pos = calc.posn(self._entity)
        # update landing graphic objects
        # self._update_landing_graphic()
    # end of _update_obj

    def get_obj(self):  # -> (any of vpython.sphere, vpython.compound)
        return self._obj
    # end of get_obj

    def relevant_range(self) -> None:
        return self._obj.radius * 2
    # end of relevant_range

    @abstractmethod
    def _draw_labels(self) -> None:
        pass
    # end of _draw_labels

    @abstractmethod
    def draw(self, entity: protos.Entity) -> None:
        pass
    # end of draw

    @abstractmethod
    def clear_trail(self) -> None:
        pass

    @abstractmethod
    def trail_option(self, stop: bool = False) -> None:
        pass
# end of class Displayable
