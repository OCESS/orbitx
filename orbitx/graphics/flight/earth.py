from typing import Optional

import vpython

from orbitx.physics import calc
from orbitx.data_structures import Entity, PhysicsState
from orbitx.graphics.flight.planet import Planet


class Earth(Planet):

    def _create_obj(self,
                    entity: Entity, origin: Entity,
                    texture: Optional[str]
                    ) -> vpython.compound:
        earth = super()._create_obj(entity, origin, texture)

        clouds_texture = texture.replace(f'{entity.name}.jpg', 'Clouds.png')
        clouds_bumpmap = texture.replace('Clouds.png', 'Clouds-bumpmap.png')
        clouds_radius = entity.r * entity.atmosphere_thickness
        earth.clouds = vpython.sphere(
            pos=earth.pos,
            axis=earth.axis,
            up=earth.up,
            radius=clouds_radius,
            texture=clouds_texture,
            bumpmap=clouds_bumpmap,
            opacity=0.1,  # Cloud layer mostly transparent
            shininess=0.1
        )

        return earth

    def _update_obj(self, entity: Entity,
                    state: PhysicsState, origin: Entity):
        super()._update_obj(entity, state, origin)
        self._obj.clouds.pos = self._obj.pos
        self._obj.clouds.axis = calc.angle_to_vpy(
            entity.heading * calc.windspeed_multiplier(entity, windspeed=100))

    def set_map_mode(self, scale_factor: float, map_mode: bool) -> None:
        super().set_map_mode(scale_factor, map_mode)
        if map_mode:
            self._obj.clouds.radius /= scale_factor
        else:
            self._obj.clouds.radius *= scale_factor
