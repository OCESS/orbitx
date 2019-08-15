"""
This modules in this subpackage implement the different OrbitX programs.
Each submodule implements a programs.Program.
"""
import argparse
from typing import Callable, List, NamedTuple


class Program(NamedTuple):  # noqa: E402
    main: Callable[[argparse.Namespace], None]
    name: str
    description: str
    argparser: argparse.ArgumentParser


from . import compat
from . import flight_training
from . import hab_flight
from . import mc_flight
from . import physics_server


# A list of all defined programs, for convenience in other code.
LISTING: List[Program] = [module.program for module in [  # type: ignore
    flight_training,
    physics_server,
    hab_flight,
    mc_flight,
    compat,
]]
