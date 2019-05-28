import vpython

from orbitx import calc
from orbitx import common
from orbitx import state
from orbitx.graphics.displayable import Displayable
from orbitx.graphics.flight_gui import FlightGui


class SpaceStation(Displayable):
    def __init__(self, entity: state.Entity, flight_gui: FlightGui) -> None:
        super(SpaceStation, self).__init__(entity, flight_gui)
        ship = vpython.cone(pos=vpython.vector(-5, 0, 0),
                            axis=vpython.vector(-5, 0, 0),
                            radius=3)
        entrance = vpython.extrusion(
            path=[vpython.vec(0, 0, 0), vpython.vec(-4, 0, 0)],
            shape=[vpython.shapes.circle(radius=3),
                   vpython.shapes.rectangle(pos=[0, 0],
                                            width=0.5,
                                            height=0.5)],
            pos=vpython.vec(-3, 0, 0))

        docking_arm = vpython.extrusion(
            path=[
                vpython.vec(0, 0, 0),
                vpython.vec(-1.5, 0, 0),
                vpython.vec(-1.5, 0.5, 0)],
            shape=[vpython.shapes.circle(radius=0.03)])

        self._obj = vpython.compound(
            [ship, entrance, docking_arm],
            make_trail=True, texture=vpython.textures.metal,
            bumpmap=vpython.bumpmaps.gravel)
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
