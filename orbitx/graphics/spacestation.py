import vpython

from orbitx import calc
from orbitx import common
from orbitx import state
from orbitx.graphics.displayable import Displayable
from orbitx.graphics.flight_gui import FlightGui


class SpaceStation(Displayable):
    def __init__(self, entity: state.Entity, flight_gui: FlightGui) -> None:
        super(SpaceStation, self).__init__(entity, flight_gui)
        texture = None
        ship = vpython.cone(pos=vpython.vector(-6, 0, 0),
                            axis=vpython.vector(-5, 0, 0),
                            radius=3, texture=texture)
        entrance = vpython.extrusion(
            path=[vpython.vec(0, 0, 0), vpython.vec(-6, 0, 0)],
            shape=[vpython.shapes.circle(radius=3),
                   vpython.shapes.rectangle(pos=[0, 0],
                                            width=0.5,
                                            height=0.5)],
            pos=vpython.vec(-3, 0, 0), texture=texture)

        arm_texture = None
        docking_arm = vpython.box(
            pos=vpython.vector(-1, 0.5, 0),
            length=0.2, height=1.2, width=0.2, texture=arm_texture)
        docking_latch = vpython.box(
            pos=vpython.vector(0, 0, 0),
            length=2, height=0.2, width=0.2, texture=arm_texture)

        self._obj = vpython.compound(
            [ship, entrance, docking_arm, docking_latch],
            make_trail=True)
        self._obj.pos = entity.screen_pos(self.flight_gui.origin())
        self._obj.axis = calc.angle_to_vpy(self._entity.heading)
        self._obj.length = entity.r * 2
        self._obj.height = entity.r * 2
        self._obj.width = entity.r * 2

        # A compound object doesn't actually have a radius, but we need to
        # monkey-patch this for when we recentre the camera, to determine the
        # relevant_range of the space station
        self._obj.radius = entity.r
        self._obj.name = self._entity.name

        self._draw_labels()
    # end of __init__

    def draw_landing_graphic(self, entity: state.Entity) -> None:
        # AYSE doesn't have landing graphics
        pass

    def _draw_labels(self) -> None:
        self._label = self._create_label()
        self._label.text_function = lambda entity: (
            f'{entity.name}\n'
            f'Fuel: {common.format_num(entity.fuel, " kg")}' +
            ('\nLanded' if entity.attached_to else '')
        )
        self._label.text = self._label.text_function(self._entity)
    # end of _draw_labels

    def draw(self, entity: state.Entity):
        self._update_obj(entity)
