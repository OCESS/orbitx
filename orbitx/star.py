from pathlib import Path

import vpython

from orbitx.planet import Planet
import orbitx.state as state


class Star(Planet):
    def __init__(self, entity: state.Entity, texture_path: Path) -> None:
        super(Star, self).__init__(entity, texture_path)
        self._obj.emissive = True  # The sun glows!
        self._lights = [vpython.local_light(pos=self._obj.pos)]
    # end of __init__

    def relevant_range(self):
        return self._obj.radius * 15000


# end of Sun
