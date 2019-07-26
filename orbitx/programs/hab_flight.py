import argparse
import atexit
import logging

from orbitx import common
from orbitx import network
from orbitx import programs
from orbitx.graphics import flight_gui

log = logging.getLogger()


name = "Habitat Flight"

description = """Connect to a running Lead Flight Server and follow along with
its simulation state. While this Mirror is running, you can pause network
updates and take control of the Habitat."""

argument_parser = argparse.ArgumentParser('habflight', description=description)
argument_parser.add_argument(
    'lead_server', type=str, nargs='?', default='localhost',
    help=(
        'Network name of the computer where the lead server is running. If the'
        ' lead server is running on the same machine, put "localhost".')
)


def main(args: argparse.Namespace):
    log.info(f'Connecting to lead server {args.lead_server}.')
    lead_server_connection = network.StateClient(
        args.lead_server, common.DEFAULT_PORT)
    state = lead_server_connection.get_state()

    gui = flight_gui.FlightGui(state, running_as_mirror=False)
    atexit.register(gui.shutdown)

    while True:
        gui.draw(state)
        # TODO: what if this fails? Set networking to False?
        state = lead_server_connection.get_state(iter(gui.pop_commands()))
        gui.rate(common.FRAMERATE)


program = programs.Program(
    name=name,
    description=description,
    main=main,
    argparser=argument_parser,
    headless=False
)
