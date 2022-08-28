import argparse
import atexit
import logging

from orbitx import common
from orbitx import programs
from orbitx.graphics.flight import flight_gui
from orbitx.network import Request, NetworkedStateClient

log = logging.getLogger('orbitx')

name = "MC Flight"

description = (
    "Connect to a Physics Server and follow along with its simulation state. "
    "You can temporarily this stop this MC Flight mirror from communicating "
    "with the Physics Server, and instead simulate its own gamma reality."
)

argument_parser = argparse.ArgumentParser('mcflight', description=description)
argument_parser.add_argument(
    'physics_server', type=str, nargs='?', default='localhost',
    help=(
        'Network name of the computer where the physics server is running. If '
        'the physics server is running on the same machine, put "localhost".')
)


def main(args: argparse.Namespace):
    networking = True  # Whether data is requested over the network

    log.info(f'Connecting to physics server {args.physics_server}.')
    lead_server_connection = NetworkedStateClient(
        Request.MC_FLIGHT, args.physics_server)
    state = lead_server_connection.get_state()
    physics_engine = lead_server_connection._caching_physics_engine

    gui = flight_gui.FlightGui(state, title=name, running_as_mirror=True)
    atexit.register(gui.shutdown)

    while True:
        old_networking = networking
        networking = gui.requesting_read_from_physics_server()
        if old_networking != networking:
            log.info(
                ('STARTED' if networking else 'STOPPED') +
                ' networking with the physics server at ' +
                args.physics_server)

        if networking:
            state = lead_server_connection.get_state()
        else:
            state = physics_engine.get_state()

        gui.draw(state)
        if not networking:
            # When we're not networking, allow user input.
            physics_engine.handle_requests(gui.pop_commands())
        gui.rate(common.FRAMERATE)


program = programs.Program(
    name=name,
    description=description,
    main=main,
    argparser=argument_parser
)
