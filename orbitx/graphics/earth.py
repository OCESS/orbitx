from typing import Optional

import vpython

from orbitx.physics import calc
from orbitx.data_structures import Entity, PhysicsState
from orbitx.graphics.threedeeobj import ThreeDeeObj


class Earth(ThreeDeeObj):

    def _create_earth(self, entity: Entity, texture: str) -> \
            vpython.sphere:
        ground = vpython.sphere(
            pos=vpython.vector(0, 0, 0),
            axis=calc.angle_to_vpy(entity.heading),
            up=vpython.vector(0, 0, 1),
            # So the planet doesn't intersect the landing graphic
            radius=entity.r * 0.9,
            make_trail=True,
            retain=10000,
            texture=texture,
            bumpmap=vpython.bumpmaps.gravel,
            shininess=0.3  # Planet.SHININESS=0.3
        )
        clouds_texture = texture.replace(f'{entity.name}.jpg', 'Clouds.png')
        clouds_bumpmap = texture.replace('Clouds.png', 'Clouds-bumpmap.png')
        if entity.atmosphere_thickness is not None:
            clouds_radius = entity.r * entity.atmosphere_thickness * 0.9
        else:
            clouds_radius = entity.r * 1.28 * 0.9
        ground.clouds = vpython.sphere(
            pos=ground.pos,
            axis=ground.axis,
            up=ground.up,
            radius=clouds_radius,
            texture=clouds_texture,
            bumpmap=clouds_bumpmap,
            opacity=0.1,  # Cloud layer mostly transparent
            shininess=0.1
        )

        return ground

    def _create_obj(self,
                    entity: Entity, origin: Entity,
                    texture: Optional[str]
                    ) -> vpython.sphere:

        assert texture is not None
        earth = self._create_earth(entity, texture)
        earth.pos = entity.screen_pos(origin)
        earth.clouds.pos = earth.pos

        return earth

    def _label_text(self, entity: Entity) -> str:
        return entity.name

    def draw(self, entity: Entity,
             state: PhysicsState, origin: Entity):
        self._update_obj(entity, state, origin)

        self._obj.clouds.pos = self._obj.pos
        self._obj.clouds.axis = calc.angle_to_vpy(entity.heading
                                                  * calc.windspeed_multiplier(entity, windspeed=100))
