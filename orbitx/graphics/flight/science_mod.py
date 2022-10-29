from typing import Optional

import vpython

from orbitx.physics import calc
from orbitx.data_structures.entity import Entity
from orbitx.graphics.flight.threedeeobj import ThreeDeeObj


class ScienceModule(ThreeDeeObj):
    SHININIESS = 0.3

    def _create_obj(
            self, entity: Entity, origin: Entity,
            texture: Optional[str]) -> vpython.sphere:
        main_body = vpython.box()
        side_panels = vpython.box(
            height=2, width=0.5, length=0.6)
        obj = vpython.compound(
            [main_body, side_panels], make_trail=True,
            texture=texture, bumpmap=vpython.textures.gravel)
        obj.pos = entity.screen_pos(origin)
        obj.axis = calc.angle_to_vpy(entity.heading)
        obj.length = entity.r * 2
        obj.height = entity.r * 2
        obj.width = entity.r * 2

        # A compound object doesn't actually have a radius, but we need to
        # monkey-patch this for when we recentre the camera, to determine the
        # relevant_range of the space station
        obj.radius = entity.r
        return obj

    def _label_text(self, entity: Entity) -> str:
        return entity.name
