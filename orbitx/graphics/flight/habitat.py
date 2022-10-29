from typing import List, Optional

import numpy as np
import vpython

from orbitx import common
from orbitx.data_structures.entity import Entity
from orbitx.data_structures.space import PhysicsState
from orbitx.graphics.flight.threedeeobj import ThreeDeeObj
from orbitx.physics import calc
from orbitx.strings import AYSE


class Habitat(ThreeDeeObj):
    BOOSTER_RADIUS = 5
    PARACHUTE_RADIUS = 20

    def _create_hab(self, entity: Entity, texture: str) -> \
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
        body_radius = entity.r / 8
        for quadrant in range(0, 4):
            # Generate four SRB bodies.
            normal = vpython.rotate(vpython.vector(0, 1, 1).hat,
                                    angle=quadrant * vpython.radians(90),
                                    axis=vpython.vector(1, 0, 0))
            boosters.append(vpython.cylinder(
                radius=self.BOOSTER_RADIUS,
                pos=(self.BOOSTER_RADIUS + body_radius) * normal)
            )
            boosters.append(vpython.cone(
                radius=self.BOOSTER_RADIUS, length=0.2,
                pos=((self.BOOSTER_RADIUS + body_radius) * normal +
                     vpython.vec(1, 0, 0)))
            )

        # Append an invisible point to shift the boosters down the fuselage.
        # For an explanation of why that matters, read the
        # ThreeDeeObj._create_obj docstring (and if that doesn't make sense,
        # get in touch with Patrick M please hello hi I'm always free!)
        boosters.append(vpython.sphere(opacity=0,
                                       pos=vpython.vec(1.2, 0, 0)))
        booster_texture = texture.replace(f'{entity.name}.jpg', 'SRB.jpg')
        hab.boosters = vpython.compound(boosters, texture=booster_texture)
        hab.boosters.length = entity.r * 2
        hab.boosters.axis = hab.axis

        parachute: List[vpython.standardAttributes] = []
        string_length = entity.r * 0.5
        parachute_texture = texture.replace(f'{entity.name}.jpg',
                                            'Parachute.jpg')
        # Build the parachute fabric.
        parachute.append(vpython.extrusion(
            path=vpython.paths.circle(radius=0.5, up=vpython.vec(-1, 0, 0)),
            shape=vpython.shapes.arc(
                angle1=vpython.radians(5), angle2=vpython.radians(95), radius=1
            ),
            pos=vpython.vec(string_length + self.PARACHUTE_RADIUS / 2, 0, 0)
        ))
        parachute[0].height = self.PARACHUTE_RADIUS * 2
        parachute[0].width = self.PARACHUTE_RADIUS * 2
        parachute[0].length = self.PARACHUTE_RADIUS
        for quadrant in range(0, 4):
            # Generate parachute attachment lines.
            string = vpython.cylinder(
                axis=vpython.vec(string_length, self.PARACHUTE_RADIUS, 0),
                radius=0.2
            )
            string.rotate(angle=(quadrant * vpython.radians(90) - vpython.radians(45)),
                          axis=vpython.vector(1, 0, 0))
            parachute.append(string)
        parachute.append(vpython.sphere(
            opacity=0,
            pos=vpython.vec(-(string_length + self.PARACHUTE_RADIUS), 0, 0)))
        hab.parachute = vpython.compound(parachute, texture=parachute_texture)
        hab.parachute.visible = False

        return hab

    def _create_obj(self,
                    entity: Entity, origin: Entity,
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
        self._minimap_canvas.append_to_caption(
            # The element styling will be removed at runtime. This just hides
            # this helptext during startup.
            "<span class='helptext' style='display: none'>"
            "This small 'minimap' shows the Habitat's orientation. The red "
            "arrow represents the Hab's velocity relative to the reference, "
            "and the gray arrow points to position of the reference."
            "</span>")

        self._small_habitat = self._create_hab(entity, texture)
        self._ref_arrow = vpython.arrow(color=vpython.color.gray(0.5))
        self._velocity_arrow = vpython.arrow(color=vpython.color.red)
        main_scene.select()

        self._broken: bool = False

        return habitat

    def _label_text(self, entity: Entity) -> str:
        label = entity.name
        if entity.broken:
            label += ' [BROKEN]'
        label += '\nFuel: ' + common.format_num(entity.fuel, " kg")
        if entity.landed_on == AYSE:
            label += '\nDocked'
        elif entity.landed():
            label += '\nLanded'
        return label

    def _update_obj(self, entity: Entity,
                    state: PhysicsState, origin: Entity):
        super()._update_obj(entity, state, origin)
        self._obj.boosters.pos = self._obj.pos
        self._obj.boosters.axis = self._obj.axis
        # Attach the parachute to the forward cone of the habitat.
        self._obj.parachute.pos = (
                self._obj.pos + calc.angle_to_vpy(entity.heading)
                * entity.r * 0.8)

        parachute_is_visible = (
                (state.craft == entity.name) and state.parachute_deployed)
        if parachute_is_visible:
            drag = calc.drag(state)
            drag_mag = np.inner(drag, drag)
        for parachute in [self._obj.parachute, self._small_habitat.parachute]:
            if not parachute_is_visible or drag_mag < 0.00001:
                # If parachute_is_visible == False, don't show the parachute.
                # If the drag is basically zero, don't show the parachute.
                parachute.visible = False
                continue

            if drag_mag > 0.1:
                parachute.width = self.PARACHUTE_RADIUS * 2
                parachute.height = self.PARACHUTE_RADIUS * 2
            else:
                # Below a certain threshold the parachute deflates.
                parachute.width = self.PARACHUTE_RADIUS
                parachute.height = self.PARACHUTE_RADIUS

            parachute.axis = -vpython.vec(*drag, 0)
            parachute.visible = True

        if not self._broken and entity.broken:
            # We weren't broken before, but looking at new data we realize
            # we're now broken. Change the habitat texture.
            new_texture = self._obj.texture.replace(
                'Habitat.jpg', 'Habitat-broken.jpg')
            assert new_texture != self._obj.texture, \
                f'{new_texture!r} == {self._obj.texture!r}'
            self._obj.texture = new_texture
            self._small_habitat.texture = new_texture
            self._broken = entity.broken
        elif self._broken and not entity.broken:
            # We were broken before, but we've repaired ourselves somehow.
            new_texture = self._obj.texture.replace(
                'Habitat-broken.jpg', 'Habitat.jpg')
            assert new_texture != self._obj.texture, \
                f'{new_texture!r} == {self._obj.texture!r}'
            self._obj.texture = new_texture
            self._small_habitat.texture = new_texture
            self._broken = entity.broken

        # Set reference and target arrows of the minimap habitat.
        same = state.reference == entity.name
        default = vpython.vector(0, 0, -1)

        ref_arrow_axis = (
                entity.screen_pos(state.reference_entity()).norm() *
                entity.r * -1.2
        )
        v = entity.v - state.reference_entity().v
        velocity_arrow_axis = \
            vpython.vector(*v, 0).norm() * entity.r

        self._ref_arrow.axis = default if same else ref_arrow_axis
        self._velocity_arrow.axis = default if same else velocity_arrow_axis
        self._small_habitat.axis = self._obj.axis
        self._small_habitat.boosters.axis = self._obj.axis

        # Invisible-ize the SRBs if we ran out.
        if state.srb_time == common.SRB_EMPTY and self._obj.boosters.visible:
            self._obj.boosters.visible = False
            self._small_habitat.boosters.visible = False

    def set_map_mode(self, scale_factor, map_mode: bool) -> None:
        """Just don't render in map mode."""

        # We can't let the radius get super small due to vpython rendering issues
        if map_mode:
            self._obj.radius *= scale_factor

        super().set_map_mode(scale_factor, map_mode)

        if not map_mode:
            self._obj.radius /= scale_factor

        self._obj.visible = not map_mode
        self._obj.boosters.visible = not map_mode
        self._obj.parachute.visible = not map_mode
