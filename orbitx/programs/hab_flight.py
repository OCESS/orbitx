import argparse
import atexit
import logging

from orbitx import common
from orbitx import network
from orbitx import programs
from orbitx.graphics import flight_gui

log = logging.getLogger()


name = "Habitat Flight"

description = (
    "Connect to a running Physics Server and provide graphical pilot control "
    "of the Physics Server."
)

argument_parser = argparse.ArgumentParser('habflight', description=description)
argument_parser.add_argument(
    'physics_server', type=str, nargs='?', default='localhost',
    help=(
        'Network name of the computer where the lead server is running. If the'
        ' lead server is running on the same machine, put "localhost".')
)


def main(args: argparse.Namespace):
    log.info(f'Connecting to physics server {args.physics_server}.')
    lead_server_connection = network.StateClient(args.physics_server)
    state = lead_server_connection.get_state()

    gui = flight_gui.FlightGui(state, running_as_mirror=False)
    atexit.register(gui.shutdown)

    while True:
        gui.draw(state)
        # TODO: what if this fails? Set networking to False?
        state = lead_server_connection.get_state(gui.pop_commands())
        gui.rate(common.FRAMERATE)


program = programs.Program(
    name=name,
    description=description,
    main=main,
    argparser=argument_parser,
    headless=False
)
