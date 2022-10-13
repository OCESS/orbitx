import argparse
import concurrent.futures
import atexit
import logging
import os
from pathlib import Path

import grpc

from orbitx import common
from orbitx import network
from orbitx import programs
from orbitx.physics.simulation import PhysicsEngine
from orbitx.graphics.server_gui import ServerGui
from orbitx.data_structures import savefile
import orbitx.orbitx_pb2_grpc as grpc_stubs

log = logging.getLogger('orbitx')

name = "Physics Server"

description = (
    "Simulate the Habitat in spaceflight with the specified savefile."
    "<br />To control this Physics Server, connect a Habitat Flight client."
    "<br />To just view the state of this Physics Server, connect an "
    "MC flight client."
    "<br />To have this Physics Server communicate with OrbitV engineering, "
    "connect a Compatibility Client."
)

argument_parser = argparse.ArgumentParser(
    'physicsserver',
    description=description.replace('<br />', '\n'))
argument_parser.add_argument(
    'loadfile', type=str, nargs='?', default='OCESS.json',
    help=(
        f'Name of the savefile to load, relative to {savefile.full_path(".")}. '
        'Should be a .json savefile written by OrbitX. '
        'Can also read OrbitV .RND savefiles.')
)


def main(args: argparse.Namespace):
    # Before you make changes to this function, keep in mind that this function
    # starts a GRPC server that runs in a separate thread!
    state_server = network.StateServer()

    loadfile: Path
    if os.path.isabs(args.loadfile):
        loadfile = Path(args.loadfile)
    else:
        # Take paths relative to 'data/saves/'
        loadfile = savefile.full_path(args.loadfile)

    physics_engine = PhysicsEngine(savefile.load_savefile(loadfile))
    initial_state = physics_engine.get_state()

    TICKS_BETWEEN_CLIENT_LIST_REFRESHES = 150
    ticks_until_next_client_list_refresh = 0

    server = grpc.server(
        concurrent.futures.ThreadPoolExecutor(max_workers=4))
    atexit.register(lambda: server.stop(grace=2))
    grpc_stubs.add_StateServerServicer_to_server(state_server, server)
    server.add_insecure_port(f'[::]:{network.DEFAULT_PORT}')
    state_server.notify_state_change(initial_state.as_proto())
    server.start()  # This doesn't block!

    gui = ServerGui()

    try:
        if args.flamegraph:
            common.start_flamegraphing()
        if args.profile:
            common.start_profiling()

        while True:
            # If we have any commands, process them immediately so input lag
            # is minimized.
            commands = state_server.pop_commands() + gui.pop_commands()
            physics_engine.handle_requests(commands)

            state = physics_engine.get_state()
            state_server.notify_state_change(state.as_proto())

            if ticks_until_next_client_list_refresh == 0:
                ticks_until_next_client_list_refresh = \
                    TICKS_BETWEEN_CLIENT_LIST_REFRESHES
                state_server.refresh_client_list()
            ticks_until_next_client_list_refresh -= 1

            gui.update(state, state_server.addr_to_connected_clients.values())
    finally:
        server.stop(grace=1)


program = programs.Program(
    name=name,
    description=description,
    main=main,
    argparser=argument_parser
)
