from . import orbitx_pb2 as protos  # physics module
from pathlib import Path
from orbitx.displayable import Displayable
import vpython
import logging
import orbitx.calculator
import orbitx.calculator as calc
import numpy as np
import math


class SpaceStation(Displayable):
    def __init__(self, entity: protos.Entity, texture_path: Path) -> None:
        super(SpaceStation, self).__init__(entity, texture_path)
        self._obj = vpython.sphere(	pos=calc.posn(entity),
                                    axis=calc.ang_pos(entity.heading),
                                    up=vpython.vector(0, 0, 1),
                                    radius=entity.r,
                                    make_trail=False,
                                    retain=10000,
                                    shininess=Displayable.PLANET_SHININIESS)
        self._obj.name = self._entity.name
        self._draw_labels()
    # end of __init__

    def _draw_labels(self) -> None:
        self._label = self._create_label()
        self._label.text_function = lambda entity: entity.name
        self._label.text = self._label.text_function(self._entity)
    # end of _draw_labels

    def draw(self, entity: protos.PhysicalState):
        self._update_obj(entity)
    # end of draw

    def clear_trail(self) -> None:
        trail = None
    # end of clear_trail

    def trail_option(self, stop: bool = False) -> None:
        trail = None
# end of class SpaceStation
