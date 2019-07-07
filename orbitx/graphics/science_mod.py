from typing import Optional

import vpython

from orbitx import calc
from orbitx import state
from orbitx.graphics.threedeeobj import ThreeDeeObj


class ScienceModule(ThreeDeeObj):
    SHININIESS = 0.3

    def _create_obj(
        self, entity: state.Entity, origin: state.Entity,
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

    def _label_text(self, entity: state.Entity) -> str:
        return entity.name
