from . import orbitx_pb2 as protos  # physics module
from pathlib import Path
from orbitx.displayable import Displayable
import vpython
import orbitx.calculator as calc
import numpy as np


class Habitat(Displayable):
    def __init__(self, entity: protos.Entity, texture_path: Path) -> None:
        super(Habitat, self).__init__(entity, texture_path)
        self._habitat_trail = None
        self._obj = self.__create_habitat()  # create Habitat object
        self._label = self._draw_labels()
    # end of __init__

    def __create_habitat(self) -> vpython.compound:
        """
                create a vpython compound object that represents our habitat.
        """
        # TODO: 1) ARROW
        body = vpython.cylinder(pos=vpython.vector(0, 0, 0),
                                axis=vpython.vector(-5, 0, 0),
                                radius=7)

        head = vpython.cone(pos=vpython.vector(0, 0, 0),
                            axis=vpython.vector(3, 0, 0),
                            radius=7)

        wing = vpython.triangle(
            v0=vpython.vertex(pos=vpython.vector(0, 0, 0)),
            v1=vpython.vertex(
                pos=vpython.vector(-5, 30, 0)),
            v2=vpython.vertex(pos=vpython.vector(-5, -30, 0)))

        wing2 = vpython.triangle(
            v0=vpython.vertex(pos=vpython.vector(0, 0, 0)),
            v1=vpython.vertex(
                pos=vpython.vector(-5, 0, 30)),
            v2=vpython.vertex(pos=vpython.vector(-5, 0, -30)))

        habitat = vpython.compound([body, head, wing, wing2])
        habitat.name = "Habitat"  # For convenient accessing later
        habitat.texture = vpython.textures.metal
        habitat.pos = calc.posn(self._entity)
        habitat.axis = calc.ang_pos(self._entity.heading)
        habitat.radius = self._entity.r / 2
        habitat.shininess = 0.1
        habitat.length = self._entity.r * 2
        habitat.arrow = calc.unit_velocity(self._entity)
        # self._habitat = _entity
        vpython.attach_arrow(habitat, 'arrow')  # scale=planet.r * 1.5)
        self._habitat_trail = vpython.attach_trail(habitat, retain=100)

        self._habitat_trail.stop()
        self._habitat_trail.clear()

        habitat.texture = self._texture
        return habitat
    # end of __create_habitat

    def _draw_labels(self) -> vpython.label:
        self._label = self._create_label()
        self._label.text_function = lambda entity: (
            f'{entity.name}\n'
            f'Fuel: {abs(round(entity.fuel, 1))} kg\n'
            f'Heading: {round(np.degrees(entity.heading))}\xb0'
        )
        self._label.text = self._label.text_function(self._entity)
        return self._label
    # end of _draw_labels

    def draw(self, entity: protos.Entity):
        self._update_obj(entity)
        self._obj.arrow = calc.unit_velocity(self._entity)
    # end of draw

    def clear_trail(self) -> None:
        self._habitat_trail.clear()
    # end of clear_trail

    def trail_option(self, stop: bool = False) -> None:
        if stop:
            self._habitat_trail.start()
        else:
            self._habitat_trail.stop()
            self._habitat_trail.clear()
# end of class Habitat
