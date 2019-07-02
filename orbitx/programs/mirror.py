import argparse
import atexit
import logging
import time

from orbitx import common
from orbitx import network
from orbitx import physics
from orbitx.graphics import flight_gui

log = logging.getLogger()


description = 'Mirror description'

argument_parser = argparse.ArgumentParser('mirror', description=description)
argument_parser.add_argument(
    'lead_server', type=str, nargs='?', default='localhost',
    help=(
        'Network name of the computer where the lead server is running. If the'
        ' lead server is running on the same machine, put "localhost".')
)


def main(args: argparse.Namespace):
    time_of_last_network_update = 0.0
    networking = True  # Whether data is requested over the network

    log.info(f'Connecting to lead server {args.lead_server}.')
    lead_server_connection = network.StateClient(
        args.lead_server, common.DEFAULT_PORT)
    state = lead_server_connection.get_state()
    physics_engine = physics.PEngine(state)

    gui = flight_gui.FlightGui(state, running_as_mirror=True)
    atexit.register(gui.shutdown)

    while True:
        old_networking = networking
        networking = gui.lead_server_communication_requested()
        if old_networking != networking:
            log.info(
                ('STARTED' if networking else 'STOPPED') +
                ' networking with the lead flight server at ' +
                args.lead_server)

        if (networking and
            time.monotonic() - time_of_last_network_update >
                common.TIME_BETWEEN_NETWORK_UPDATES):
            # Our state is stale, get the latest update
            # TODO: what if this fails? Set networking to False?
            state = lead_server_connection.get_state()
            physics_engine.set_state(state)
            time_of_last_network_update = time.monotonic()
        else:
            state = physics_engine.get_state()

        gui.draw(state)
        if not networking:
            # When we're not networking, allow user input.
            user_commands = gui.pop_commands()
            for request in user_commands:
                physics_engine.handle_request(request)
        gui.rate(common.FRAMERATE)


Mirror = common.Program(
    name='Mirror',
    description=description,
    main=main,
    argparser=argument_parser
)
