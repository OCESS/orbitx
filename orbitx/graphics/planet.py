from typing import Optional

import vpython

from orbitx.physics import calc
from orbitx.data_structures import Entity
from orbitx.graphics.threedeeobj import ThreeDeeObj


class Planet(ThreeDeeObj):
    SHININIESS = 0.3

    def _create_obj(
            self, entity: Entity, origin: Entity,
            texture: Optional[str]) -> vpython.sphere:
        return vpython.sphere(
            pos=entity.screen_pos(origin),
            axis=calc.angle_to_vpy(entity.heading),
            up=vpython.vector(0, 0, 1),
            # So the planet doesn't intersect the landing graphic
            radius=entity.r * 0.9,
            make_trail=True,
            retain=10000,
            texture=texture,
            bumpmap=vpython.bumpmaps.gravel,
            shininess=Planet.SHININIESS
        )

    def _label_text(self, entity: Entity) -> str:
        return entity.name
