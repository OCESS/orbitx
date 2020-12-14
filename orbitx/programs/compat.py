"""
main() for the compatibility server, an intermediary between orbitx and orbit.

Communicates to orbitx with GRPC, and to orbit using orbit_communication.py.
"""

import argparse
import logging
from datetime import datetime
from pathlib import Path

import grpc

from orbitx import network
from orbitx import orbitv_file_interface
from orbitx import programs
from orbitx.graphics.compat_gui import CompatGui, StartupFailedGui

log = logging.getLogger()

name = "Compatibility Client"

description = (
    "Pretends to be a running OrbitV Habitat flight program. Communicates to "
    "OrbitV by writing an OSBACKUP.RND file, and receives communications from "
    "OrbitV by reading an ORBITSSE.RND file.<br />"
    "Recommended use is to run this on the machine that ServerV.exe "
    "expects OrbitV hab piloting to be, and setting the --piloting flag to "
    "the directory that OrbitV hab piloting would usually run in."
)

argument_parser = argparse.ArgumentParser(
    'compat', description=description.replace('<br />', '\n'))
argument_parser.add_argument(
    "--piloting", default="orbit-files/",
    help="Path to , "
         "containing OSbackup.RND and ORBITSSE.RND"
)
argument_parser.add_argument(
    "--physics-server", default="localhost",
    help="network name of the physics server"
)


def main(args: argparse.Namespace):
    orbitx_connection = network.NetworkedStateClient(
        network.Request.COMPAT, args.physics_server)
    log.info(f'Connecting to OrbitX Physics Server: {args.physics_server}')

    intermediary = orbitv_file_interface.OrbitVIntermediary(
        Path(args.piloting))

    try:
        # Make sure we have a connection before continuing.
        orbitx_connection.get_state(
            [network.Request(ident=network.Request.NOOP)])
    except grpc.RpcError as err:
        log.error(f'Could not connect to Physics Server: {err.code()}')
        StartupFailedGui(args.physics_server, err)
        return

    gui = CompatGui(args.physics_server, intermediary)

    last_orbitsse_modified_time = 0.0
    last_orbitsse_read_datetime = datetime.fromtimestamp(0)

    try:
        while True:
            orbitsse_modified_time = intermediary.orbitsse.stat().st_mtime
            if orbitsse_modified_time == last_orbitsse_modified_time:
                # We've already seen this version of ORBITSSE.RND.
                update = network.Request(ident=network.Request.NOOP)
            else:
                last_orbitsse_modified_time = orbitsse_modified_time
                last_orbitsse_read_datetime = datetime.now()
                update = intermediary.read_engineering_update()

            state = orbitx_connection.get_state([update])
            intermediary.write_state(state)
            gui.update(
                update, state._entity_names, last_orbitsse_read_datetime)
    except grpc.RpcError as err:
        log.error(
            f'Got response code {err.code()} from orbitx, shutting down')
        gui.notify_shutdown(err)


program = programs.Program(
    name=name,
    description=description,
    main=main,
    argparser=argument_parser
)
