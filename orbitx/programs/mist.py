"""
main() for MIST, a program for monitoring astronauts' vitals.

Communicates to orbitx with GRPC.
"""

import argparse
import logging
import random
import time

import grpc

from orbitx import network
from orbitx import programs
from orbitx.graphics.compat_gui import StartupFailedGui

log = logging.getLogger()


name = "MIST"

description = (
    "A view into the astronauts' vitals."
)

argument_parser = argparse.ArgumentParser(
    'mist', description=description.replace('<br />', '\n'))
argument_parser.add_argument(
    "--physics-server", default="localhost",
    help="network name of the physics server"
)


def main(args: argparse.Namespace):
    orbitx_connection = network.StateClient(
        network.Request.MIST, args.physics_server)
    log.info(f'Connecting to OrbitX Physics Server: {args.physics_server}')

    try:
        # Make sure we have a connection before continuing.
        orbitx_connection.get_state(
            [network.Request(ident=network.Request.NOOP)])
    except grpc.RpcError as err:
        log.error(f'Could not connect to Physics Server: {err.code()}')
        StartupFailedGui(args.physics_server, err)
        return

    random.seed()

    try:
        while True:
            print(random.choice(['ASTRONAUT STATUS: DYING',
                                 'astronaut status: okay']))
            print(orbitx_connection.get_state(
                  [network.Request(ident=network.Request.NOOP)])['Earth'].pos)
            time.sleep(1)
    except grpc.RpcError as err:
        log.error(
            f'Got response code {err.code()} from orbitx, shutting down')


program = programs.Program(
    name=name,
    description=description,
    main=main,
    argparser=argument_parser
)