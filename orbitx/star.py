from . import orbitx_pb2 as protos  # physics module
from pathlib import Path
from orbitx.displayable import Displayable
from orbitx.planet import Planet
import vpython
import logging
import orbitx.calculator
import orbitx.calculator as calc
import numpy as np
import math


class Star(Planet):
    def __init__(self, entity: protos.Entity, texture_path: Path) -> None:
        super(Star, self).__init__(entity, texture_path)
        self._obj.emissive = True  # The sun glows!
        self._lights = [vpython.local_light(pos=self._obj.pos)]
    # end of __init__

    def relevant_range(self):
        return self._obj.radius * 15000


# end of Sun
