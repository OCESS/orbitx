"""
This modules in this subpackage implement the different OrbitX programs.
Each submodule implements a programs.Program.
"""
from typing import List

from . import compat
from . import flight_training
from . import hab_flight
from . import mc_flight
from . import physics_server
from . import mist
from . import hab_eng
from orbitx.common import Program


# A list of all defined programs, for convenience in other code.
LISTING: List[Program] = [module.program for module in [  # type: ignore
    flight_training,
    physics_server,
    hab_flight,
    mc_flight,
    compat,
    mist,
    hab_eng,
]]
