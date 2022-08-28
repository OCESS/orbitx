import argparse
import atexit
import logging

from orbitx import common
from orbitx import programs
from orbitx.graphics.flight import flight_gui
from orbitx.network import Request, NetworkedStateClient

log = logging.getLogger('orbitx')

name = "Habitat Flight"

description = (
    "Connect to a running Physics Server and provide graphical pilot control "
    "of the Physics Server."
)

argument_parser = argparse.ArgumentParser('habflight', description=description)
argument_parser.add_argument(
    'physics_server', type=str, nargs='?', default='localhost',
    help=(
        'Network name of the computer where the physics server is running. If '
        'the physics server is running on the same machine, put "localhost".')
)


def main(args: argparse.Namespace):
    log.info(f'Connecting to physics server {args.physics_server}.')
    lead_server_connection = NetworkedStateClient(
        Request.HAB_FLIGHT, args.physics_server)
    state = lead_server_connection.get_state()

    gui = flight_gui.FlightGui(state, title=name, running_as_mirror=False)
    atexit.register(gui.shutdown)

    while True:
        gui.draw(state)

        user_commands = gui.pop_commands()

        state = lead_server_connection.get_state(user_commands)

        gui.rate(common.FRAMERATE)


program = programs.Program(
    name=name,
    description=description,
    main=main,
    argparser=argument_parser
)
