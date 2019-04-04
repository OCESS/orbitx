import vpython

from orbitx import state
from orbitx.flight_gui import FlightGui
from orbitx.planet import Planet


class Star(Planet):
    def __init__(self, entity: state.Entity, flight_gui: FlightGui) -> None:
        super(Star, self).__init__(entity, flight_gui)
        self._obj.emissive = True  # The sun glows!
        self._lights = [vpython.local_light(pos=self._obj.pos)]
    # end of __init__

    def relevant_range(self):
        return self._obj.radius * 15000


# end of Sun
