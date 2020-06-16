"""
This modules in this subpackage implement the different OrbitX programs.
Each submodule implements a programs.Program.
"""
import argparse
import warnings
from typing import Callable, List, NamedTuple

with warnings.catch_warnings():
	warnings.simplefilter('ignore')
	from grpc_channelz.v1 import channelz_pb2

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
