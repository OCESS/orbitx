import vpython
import numpy as np

from orbitx import calc
from orbitx import common
from orbitx import state
from orbitx.displayable import Displayable
from orbitx.flight_gui import FlightGui


class SpaceStation(Displayable):
    def __init__(self, entity: state.Entity, flight_gui: FlightGui) -> None:
        super(SpaceStation, self).__init__(entity, flight_gui)
        _pos = entity.screen_pos(self.flight_gui.origin())
        _radius = entity.r
        _axis = calc.angle_to_vpy(self._entity.heading + np.pi)
        ship = vpython.cone(pos=vpython.vector(2, 0, 0),
                            axis=vpython.vector(-8, 0, 0),
                            radius=3,
                            opacity=0.7)
        entrance = vpython.extrusion(
            path=[vpython.vec(0, 0, 0), vpython.vec(-4, 0, 0)],
            shape=[vpython.shapes.circle(radius=1.5),
                   vpython.shapes.rectangle(pos=[0, -0.3],
                                            width=1.5,
                                            height=1.5)],
            pos=vpython.vec(0, 0, 0))  # position

        self._obj = vpython.compound([ship, entrance])
        self._obj.pos = _pos
        self._obj.axis = _axis
        self._obj.radius = _radius * 2
        self._obj.length = _radius * 2
        self._obj.height = _radius * 2
        self._obj.width = _radius * 2

        self._obj.name = self._entity.name

        self._station_trail = vpython.attach_trail(self._obj, retain=100)

        self._station_trail.stop()
        self._station_trail.clear()

        self._draw_labels()
    # end of __init__

    def draw_landing_graphic(self, entity: state.Entity) -> None:
        # AYSE doesn't have landing graphics
        pass

    def _draw_labels(self) -> None:
        self._label = self._create_label()
        self._label.text_function = lambda entity: (
            f'{entity.name}\n'
            f'Fuel: {common.format_num(entity.fuel)} kg'
        )
        self._label.text = self._label.text_function(self._entity)
    # end of _draw_labels

    def draw(self, entity: state.Entity):
        self._update_obj(entity)
    # end of draw

    def clear_trail(self) -> None:
        self._station_trail.clear()

    def make_trail(self, trails: bool) -> None:
        self.clear_trail()
        if trails:
            self._station_trail.start()
        else:
            self._station_trail.stop()

# end of class SpaceStation
