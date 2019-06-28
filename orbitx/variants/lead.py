import argparse
import concurrent.futures
import atexit
import logging
import os
from pathlib import Path
from typing import List

import grpc

from orbitx import common
from orbitx import network
from orbitx import physics
from orbitx.graphics import flight_gui
import orbitx.orbitx_pb2_grpc as grpc_stubs

log = logging.getLogger()

argument_parser = argparse.ArgumentParser()
argument_parser.add_argument(
    'loadfile', type=str, nargs='?', default='OCESS.json',
    help=(
        'Name of the savefile to be loaded. Should be a .json'
        ' file, in a format that OrbitX expects.')
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

    log.info(f'Loading save at {loadfile}')
    physics_engine = physics.PEngine(common.load_savefile(loadfile))

    gui = flight_gui.FlightGui(physics_engine.get_state(),
                               running_as_mirror=False)
    atexit.register(gui.shutdown)

    server = grpc.server(
        concurrent.futures.ThreadPoolExecutor(max_workers=4))
    atexit.register(lambda: server.stop(grace=2))
    grpc_stubs.add_StateServerServicer_to_server(state_server, server)
    server.add_insecure_port(f'[::]:{common.DEFAULT_LEAD_SERVER_PORT}')
    server.start()  # This doesn't block!

    if args.profile:
        common.start_profiling()

    try:
        while True:
            user_commands: List[network.Request] = []
            state = physics_engine.get_state()
            state_server.notify_state_change(state.as_proto())

            user_commands += gui.pop_commands()
            user_commands += state_server.pop_commands()

            # If we have any commands, process them so the simthread has as
            # much time as possible to restart before next update.
            for command in user_commands:
                if command.ident == network.Request.NOOP:
                    continue
                log.info(f'Got command: {command}')
                physics_engine.handle_request(command)

            gui.draw(state)
            gui.rate(common.FRAMERATE)
    except KeyboardInterrupt:
        raise
    except Exception:
        gui.ungraceful_shutdown()
        server.stop(grace=0)
        raise
