from typing import Optional

import vpython

from orbitx import state
from orbitx.graphics.planet import Planet


class Star(Planet):

    def _create_obj(
        self, entity: state.Entity, origin: state.Entity,
            texture: Optional[str]) -> vpython.sphere:
        obj = super(Star, self)._create_obj(entity, origin, texture)
        obj.emissive = True  # The sun glows!
        self._light = vpython.local_light(pos=obj.pos)
        return obj

    def relevant_range(self):
        return self._obj.radius * 15000

    def _update_obj(self, entity: state.Entity,
                    state: state.PhysicsState, origin: state.Entity) -> None:
        super(Star, self)._update_obj(entity, state, origin)
        # Also make sure to change the position of the light
        self._light.pos = self._obj.pos
