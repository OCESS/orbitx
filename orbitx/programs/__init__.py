"""
This modules in this subpackage implement the different OrbitX programs.
Each submodule implements a programs.Program.
"""
import argparse
from typing import Callable, List, NamedTuple


class Program(NamedTuple):
    main: Callable[[argparse.Namespace], None]
    name: str
    description: str
    argparser: argparse.ArgumentParser


from . import compat  # noqa: E402
from . import flight_training  # noqa: E402
from . import hab_flight  # noqa: E402
from . import mc_flight  # noqa: E402
from . import physics_server  # noqa: E402


# A list of all defined programs, for convenience in other code.
LISTING: List[Program] = [module.program for module in [  # type: ignore
    flight_training,
    physics_server,
    hab_flight,
    mc_flight,
    compat,
]]
