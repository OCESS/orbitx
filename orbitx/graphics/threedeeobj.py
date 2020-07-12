import logging
from abc import ABCMeta
from abc import abstractmethod
from pathlib import Path
from typing import Optional, Union

import vpython

from orbitx.physics import calc
from orbitx.data_structures import Entity, PhysicsState

log = logging.getLogger()


class ThreeDeeObj(metaclass=ABCMeta):

    @abstractmethod
    def _create_obj(self,
                    entity: Entity, origin: Entity,
                    texture: Optional[str]
                    ) -> Union[vpython.sphere, vpython.compound]:
        """Create a 3D object, like a planet, a star, or a spaceship, using
        vpython and return it. It will be rotated etc. elsewhere, don't worry
        about that. Just make a cool object!

        Note when drawing new fancy objects and when you eventually use the
        vpython.compound object:
        To make a vpython.compound object (say, obj = vpython.compound(shapes))
        have a length equal to the size of an entity's diameter, you'll end up
        setting obj.length = entity.r * 2, or something similar.
        But the shapes that you wrap in the vpython.compound object will also
        be stretched in unexpected ways. If you can't make sense of it,
        consider the following example:

        a = vpython.cylinder(length=1)
        b = vpython.sphere(radius=0.2)
        compound = vpython.compound([a, b])
        compound.length = my_length

        will visually look exactly the same as if `a` and `b` both had exactly
        ten times the length and radius, or thirty times the length and radius.
        The dimensions of the individual shapes in a compound object don't
        matter, it's the _proportion_ of the shapes to each other.
        """
        pass

    @abstractmethod
    def _label_text(self, entity: Entity) -> str:
        """Return text that should be put in the label for a 3d object.
        This method is evaluated every frame using the newest physics data."""
        pass

    # When creating a new 3D object, usually you don't have to worry about
    # anything below here. All you have to do is override the three above
    # methods in your derived class.
    # Sometimes you'll want to do something special. But most of the time, it's
    # not needed.

    def __init__(self, entity: Entity,
                 origin: Entity, texture_path: Path) -> None:
        texture_path = texture_path / (entity.name + '.jpg')

        texture = str(texture_path) if texture_path.is_file() else None
        self._obj = self._create_obj(entity, origin, texture)
        assert self._obj is not None

        self._label = vpython.label(
            pos=self._obj.pos, xoffset=10, yoffset=10, border=4, font='sans',
            text=self._label_text(entity))

        # The object is made smaller by greater values of this.
        # The use of _scale_factor is when OrbitX goes into map mode.
        self._scale_factor = 1

    def _show_hide_label(self) -> None:
        self._label.visible = not self._label.visible

    def _update_obj(self, entity: Entity,
                    state: PhysicsState, origin: Entity) -> None:
        # update planet objects
        self._obj.pos = entity.screen_pos(origin) / self._scale_factor
        self._obj.axis = calc.angle_to_vpy(entity.heading)

        # update label objects
        self._label.text = self._label_text(entity)
        self._label.pos = entity.screen_pos(origin) / self._scale_factor

    def relevant_range(self) -> float:
        return self._obj.radius * 2

    def draw(self, entity: Entity,
             state: PhysicsState, origin: Entity):
        self._update_obj(entity, state, origin)

    def clear_trail(self) -> None:
        self._obj.clear_trail()

    def make_trail(self, trails: bool) -> None:
        self.clear_trail()
        self._obj.make_trail = trails

    def set_map_mode(self, scale_factor: float, map_mode: bool) -> None:
        """Scales down the object to a much smaller size, which is easier to
        render."""
        if map_mode:
            self._scale_factor = scale_factor
            self._obj.radius /= scale_factor
        else:
            self._scale_factor = 1
            self._obj.radius *= scale_factor
