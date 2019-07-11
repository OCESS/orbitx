from typing import List, Optional

import vpython

from orbitx import calc
from orbitx import common
from orbitx import state
from orbitx.graphics.threedeeobj import ThreeDeeObj


class Habitat(ThreeDeeObj):

    def _create_hab(self, entity: state.Entity, texture: str) -> \
            vpython.compound:
        def vertex(x: float, y: float, z: float) -> vpython.vertex:
            return vpython.vertex(pos=vpython.vector(x, y, z))

        # See the docstring of ThreeDeeObj._create_obj for why the dimensions
        # that define the shape of the habitat will not actually directly
        # translate to world-space.

        body = vpython.cylinder(
            pos=vpython.vec(0, 0, 0), axis=vpython.vec(-5, 0, 0), radius=10)
        head = vpython.cone(
            pos=vpython.vec(0, 0, 0), axis=vpython.vec(2, 0, 0), radius=10)
        wing = vpython.triangle(
            v0=vertex(0, 0, 0), v1=vertex(-5, 30, 0), v2=vertex(-5, -30, 0))
        wing2 = vpython.triangle(
            v0=vertex(0, 0, 0), v1=vertex(-5, 0, 30), v2=vertex(-5, 0, -30))

        hab = vpython.compound([body, head, wing, wing2],
                               make_trail=True, texture=texture)
        hab.axis = calc.angle_to_vpy(entity.heading)
        hab.radius = entity.r / 2
        hab.shininess = 0.1
        hab.length = entity.r * 2

        boosters: List[vpython.cylinder] = []
        booster_radius = 5
        body_radius = entity.r / 15
        for quadrant in range(0, 4):
            # Generate four SRB bodies.
            normal = vpython.rotate(vpython.vector(0, 1, 1),
                                    angle=quadrant * vpython.radians(90),
                                    axis=vpython.vector(1, 0, 0))
            boosters.append(vpython.cylinder(
                radius=booster_radius,
                pos=(booster_radius + body_radius) * normal)
            )
            boosters.append(vpython.cone(
                radius=booster_radius, length=0.2,
                pos=(booster_radius + body_radius) * normal +
                vpython.vec(1, 0, 0))
            )

        # Append an invisible point to shift the boosters down the fuselage.
        # For an explanation of why that matters, read the
        # ThreeDeeObj._create_obj docstring (and if that doesn't make sense,
        # get in touch with Patrick M please hello hi I'm always free!)
        boosters.append(vpython.sphere(radius=1, opacity=0,
                                       pos=vpython.vec(1.2, 0, 0)))
        booster_texture = texture.replace(f'{entity.name}.jpg', 'SRB.jpg')
        hab.boosters = vpython.compound(boosters, texture=booster_texture)
        hab.boosters.length = entity.r * 2
        hab.boosters.axis = hab.axis

        parachute: List[vpython.standardAttributes] = []
        parachute_radius = 20
        string_length = entity.r * 1.2
        parachute_texture = texture.replace(f'{entity.name}.jpg',
                                            'Parachute.jpg')
        # Build the parachute fabric.
        parachute.append(vpython.extrusion(
            path=vpython.paths.circle(radius=0.5, up=vpython.vec(0, -1, 0)),
            shape=vpython.shapes.arc(
                angle1=vpython.radians(5), angle2=vpython.radians(95), radius=1
            ),
            pos=vpython.vec(0, string_length + parachute_radius / 2, 0)
        ))
        parachute[0].length = parachute_radius * 2
        parachute[0].width = parachute_radius * 2
        parachute[0].height = parachute_radius
        for quadrant in range(0, 4):
            # Generate parachute attachment lines.
            string = vpython.cylinder(
                axis=vpython.vec(parachute_radius, string_length, 0),
                radius=0.2
            )
            string.rotate(angle=quadrant * vpython.radians(90),
                          axis=vpython.vector(0, 1, 0))
            parachute.append(string)
        hab.parachute = vpython.compound(parachute, texture=parachute_texture)

        return hab

    def _create_obj(self,
                    entity: state.Entity, origin: state.Entity,
                    texture: Optional[str]
                    ) -> vpython.compound:
        """Creates the habitat, and also a new minimap scene and habitat."""
        assert texture is not None
        habitat = self._create_hab(entity, texture)
        habitat.pos = entity.screen_pos(origin)

        main_scene = vpython.canvas.get_selected()
        self._minimap_canvas = vpython.canvas(
            width=200, height=150, userspin=False, userzoom=False,
            up=common.DEFAULT_UP, forward=common.DEFAULT_FORWARD)

        self._small_habitat = self._create_hab(entity, texture)
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
             '\nLanded' if entity.landed() else '')
        )

    def draw(self, entity: state.Entity,
             state: state.PhysicsState, origin: state.Entity):
        self._update_obj(entity, state, origin)
        self._obj.boosters.pos = self._obj.pos
        self._obj.boosters.axis = self._obj.axis
        #self._obj.parachute.pos = self._obj.pos

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
        self._small_habitat.boosters.axis = self._obj.axis

        # Invisibile-ize the SRBs if we ran out.
        if state.srb_time == common.SRB_EMPTY and self._obj.boosters.visible:
            self._obj.boosters.visible = False
            self._small_habitat.boosters.visible = False
