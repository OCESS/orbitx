from typing import Optional

import vpython

from orbitx import calc
from orbitx import common
from orbitx import state
from orbitx.graphics.threedeeobj import ThreeDeeObj


class Habitat(ThreeDeeObj):

    def _create_hab(self, entity: state.Entity) -> vpython.compound:
        # Change which scene we're drawing a new habitat in
        def vertex(x: float, y: float, z: float) -> vpython.vertex:
            return vpython.vertex(pos=vpython.vector(x, y, z))

        body = vpython.cylinder(
            pos=vpython.vec(0, 0, 0), axis=vpython.vec(-5, 0, 0), radius=10)
        head = vpython.cone(
            pos=vpython.vec(0, 0, 0), axis=vpython.vec(3, 0, 0), radius=10)
        wing = vpython.triangle(
            v0=vertex(0, 0, 0), v1=vertex(-5, 30, 0), v2=vertex(-5, -30, 0))
        wing2 = vpython.triangle(
            v0=vertex(0, 0, 0), v1=vertex(-5, 0, 30), v2=vertex(-5, 0, -30))

        hab = vpython.compound([body, head, wing, wing2], make_trail=True)
        hab.texture = vpython.textures.metal
        hab.axis = calc.angle_to_vpy(entity.heading)
        hab.radius = entity.r / 2
        hab.shininess = 0.1
        hab.length = entity.r * 2
        hab.color = vpython.color.cyan
        return hab

    def _create_obj(self,
                    entity: state.Entity, origin: state.Entity,
                    texture: Optional[str]
                    ) -> vpython.compound:
        """Creates the habitat, and also a new minimap scene and habitat."""
        self._srb_time = -1
        habitat = self._create_hab(entity)
        habitat.pos = entity.screen_pos(origin)

        main_scene = vpython.canvas.get_selected()
        self._minimap_canvas = vpython.canvas(
            width=200, height=150, userspin=False, userzoom=False,
            up=common.DEFAULT_UP, forward=common.DEFAULT_FORWARD)

        self._small_habitat = self._create_hab(entity)
        self._ref_arrow = vpython.arrow(color=vpython.color.gray(0.5))
        self._velocity_arrow = vpython.arrow(color=vpython.color.red)
        main_scene.select()

        return habitat

    def draw_landing_graphic(self, entity: state.Entity) -> None:
        # Habitats don't have landing graphics
        pass

    def _label_text(self, entity: state.Entity) -> str:
        return (
            f'{entity.name}\n'
            f'Fuel: {common.format_num(entity.fuel, " kg")}' +
            ('\nDocked' if entity.landed_on == common.AYSE else
             '\nLanded' if entity.landed() else '') +
            (f'\nSRB time: {self._srb_time}' if self._srb_time > 0 else '')
        )

    def draw(self, entity: state.Entity,
             state: state.PhysicsState, origin: state.Entity):
        # Hacky sorry
        self._srb_time = state.srb_time
        self._update_obj(entity, state, origin)
        same = state.reference == entity.name
        default = vpython.vector(0, 0, -1)

        ref_arrow_axis = (
            entity.screen_pos(state.reference_entity()).norm() *
            entity.r * -1.2
        )
        v = entity.v - state.reference_entity().v
        velocity_arrow_axis = \
            vpython.vector(v[0], v[1], 0).norm() * entity.r

        self._ref_arrow.axis = default if same else ref_arrow_axis
        self._velocity_arrow.axis = default if same else velocity_arrow_axis
        self._small_habitat.axis = self._obj.axis
