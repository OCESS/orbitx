import argparse
import atexit
import logging
import time

from orbitx import common
from orbitx import network
from orbitx import physics
from orbitx import programs
from orbitx.graphics import flight_gui
from orbitx.network import Request

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
        'Network name of the computer where the physics server is running. If '
        'the physics server is running on the same machine, put "localhost".')
)


def main(args: argparse.Namespace):
    log.info(f'Connecting to physics server {args.physics_server}.')
    time_of_next_network_update = 0.0
    lead_server_connection = network.StateClient(
        Request.HAB_FLIGHT, args.physics_server)
    state = lead_server_connection.get_state()
    physics_engine = physics.PhysicsEngine(state)

    gui = flight_gui.FlightGui(state, title=name, running_as_mirror=False)
    atexit.register(gui.shutdown)

    while True:
        gui.draw(state)

        user_commands = gui.pop_commands()
        current_time = time.monotonic()

        # If there are user commands or we've gone a while since our last
        # contact with the physics server, request an update.
        if user_commands or current_time > time_of_next_network_update:
            # Our state is stale, get the latest update
            # TODO: what if this fails? Do anything smarter than an exception?
            state = lead_server_connection.get_state(user_commands)
            physics_engine.set_state(state)
            if len(user_commands) == 0:
                time_of_next_network_update = (
                        current_time + common.TIME_BETWEEN_NETWORK_UPDATES
                )
            else:
                # If we sent a user command, still ask for an update soon so
                # the user input can be reflected in hab flight's GUI as soon
                # as possible.
                # Magic number alert! The constant we add should be enough that
                # the physics server has had enough time to simulate the effect
                # of our input, but we should minimize the constant to minimize
                # input lag.
                time_of_next_network_update = current_time + 0.15
        else:
            state = physics_engine.get_state()

        gui.rate(common.FRAMERATE)


program = programs.Program(
    name=name,
    description=description,
    main=main,
    argparser=argument_parser
)
