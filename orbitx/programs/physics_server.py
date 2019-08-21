import argparse
import concurrent.futures
import atexit
import logging
import os
from pathlib import Path

import grpc

from orbitx import common
from orbitx import network
from orbitx import physics
from orbitx import programs
from orbitx.graphics.server_gui import ServerGui
import orbitx.orbitx_pb2_grpc as grpc_stubs

log = logging.getLogger()


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
        f'Name of the savefile to load, relative to {common.savefile(".")}. '
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
        loadfile = common.savefile(args.loadfile)

    physics_engine = physics.PEngine(common.load_savefile(loadfile))
    initial_state = physics_engine.get_state()

    server = grpc.server(
        concurrent.futures.ThreadPoolExecutor(max_workers=4),
        options=network.ENABLE_CHANNELZ)
    atexit.register(lambda: server.stop(grace=2))
    grpc_stubs.add_StateServerServicer_to_server(state_server, server)
    server.add_insecure_port(f'[::]:{network.DEFAULT_PORT}')
    state_server.notify_state_change(initial_state.as_proto())
    server.start()  # This doesn't block!

    gui = ServerGui(loadfile)

    try:
        if args.flamegraph:
            common.start_flamegraphing()
        if args.profile:
            common.start_profiling()

        while True:
            state = physics_engine.get_state()
            state_server.notify_state_change(state.as_proto())

            # If we have any commands, process them so the simthread has as
            # much time as possible to restart before next update.
            commands = state_server.pop_commands() + gui.pop_commands()
            physics_engine.handle_requests(commands)

            gui.update(state, state_server.client_types)
    finally:
        server.stop(grace=1)


program = programs.Program(
    name=name,
    description=description,
    main=main,
    argparser=argument_parser
)
