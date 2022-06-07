from typing import Optional

import vpython

from orbitx.physics import calc
from orbitx import common
from orbitx.data_structures.entity import Entity
from orbitx.graphics.flight.threedeeobj import ThreeDeeObj


class Ayse(ThreeDeeObj):
    def _create_obj(self,
                    entity: Entity, origin: Entity,
                    texture_path: Optional[str]) -> vpython.sphere:
        ship = vpython.cone(pos=vpython.vector(5, 0, 0),
                            axis=vpython.vector(5, 0, 0),
                            radius=3)
        entrance = vpython.extrusion(
            path=[vpython.vec(0, 0, 0), vpython.vec(4, 0, 0)],
            shape=[vpython.shapes.circle(radius=3),
                   vpython.shapes.rectangle(pos=[0, 0],
                                            width=0.5,
                                            height=0.5)],
            pos=vpython.vec(3, 0, 0))

        docking_arm = vpython.extrusion(
            path=[
                vpython.vec(0, 0, 0),
                vpython.vec(1.5, 0, 0),
                vpython.vec(1.5, 0.5, 0)],
            shape=[vpython.shapes.circle(radius=0.03)])

        obj = vpython.compound(
            [ship, entrance, docking_arm],
            make_trail=True, texture=vpython.textures.metal,
            bumpmap=vpython.bumpmaps.gravel)
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
        return (
                f'{entity.name}\n'
                f'Fuel: {common.format_num(entity.fuel, " kg")}' +
                ('\nLanded' if entity.landed() else '')
        )

    def set_map_mode(self, scale_factor, map_mode: bool) -> None:
        """Just don't render in map mode."""

        # We can't let the radius get super small due to vpython rendering issues
        if map_mode:
            self._obj.radius *= scale_factor

        super().set_map_mode(scale_factor, map_mode)

        if not map_mode:
            self._obj.radius /= scale_factor

        self._obj.visible = not map_mode
