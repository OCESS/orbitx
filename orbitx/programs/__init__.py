"""
This modules in this subpackage implement the different OrbitX programs.
Each submodule implements a programs.Program.

- programs.compat implements a compatibility server with OrbitV,
    reading OrbitV binary files and sending network updates to OrbitX
- programs.lead implements the lead server, which simulates the physical flight
    state and sends out updates to anyone who cares
- programs.mirror implements the mirror server, which by default follows a lead
    server in a read-only mode. It can stop getting network updates and
    continue physical simulation by itself.
"""
import argparse
from typing import Callable, List, NamedTuple


class Program(NamedTuple):  # noqa: E402
    main: Callable[[argparse.Namespace], None]
    name: str
    description: str
    argparser: argparse.ArgumentParser
    headless: bool


from . import compat
from . import flight_training
from . import hab_flight
from . import mc_flight
from . import physics_server


# A list of all defined programs, for convenience in other code.
LISTING: List[Program] = [module.program for module in [  # type: ignore
    compat, flight_training, hab_flight, mc_flight, physics_server
]]
