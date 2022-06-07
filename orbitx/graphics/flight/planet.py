from typing import Optional

import vpython

from orbitx.common import DEFAULT_FORWARD, DEFAULT_UP
from orbitx.physics import calc
from orbitx.data_structures.entity import Entity
from orbitx.graphics.flight.threedeeobj import ThreeDeeObj


class Planet(ThreeDeeObj):
    SHININIESS = 0.3

    def _create_obj(
            self, entity: Entity, origin: Entity,
            texture: Optional[str]) -> vpython.sphere:
        return vpython.sphere(
            pos=entity.screen_pos(origin),
            axis=calc.angle_to_vpy(entity.heading),
            up=DEFAULT_UP,
            forward=DEFAULT_FORWARD,
            radius=entity.r,
            make_trail=True,
            retain=10000,
            texture=texture,
            bumpmap=vpython.bumpmaps.gravel,
            shininess=Planet.SHININIESS
        )

    def _label_text(self, entity: Entity) -> str:
        return entity.name
