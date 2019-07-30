"""
main() for the compatibility server, an intermediary between orbitx and orbit.

Communicates to orbitx with GRPC, and to orbit using orbit_communication.py.
"""

import argparse
import logging
import time
from pathlib import Path

import grpc

from orbitx import network
from orbitx import orbitv_file_interface
from orbitx import programs
from orbitx.network import Request

log = logging.getLogger()


name = "Compatibility Client"

description = (
    "Communicate between a running OrbitV engineering program and an OrbitX "
    "Physics Server."
)

argument_parser = argparse.ArgumentParser('compat', description=description)
argument_parser.add_argument(
    "--engineering", default="orbit-files/",
    help="Path to engineering, "
         "containing OSbackup.RND and ORBITSSE.RND"
)
argument_parser.add_argument(
    "--physics-server", default="localhost",
    help="network name of piloting client"
)


def main(args: argparse.Namespace):
    orbitx_connection = network.StateClient(
        Request.COMPAT, args.physics_server)
    log.info(f'Connected to OrbitX Physics Server: {args.physics_server}')
    assert Path(args.engineering).exists

    osbackup = Path(args.engineering) / 'OSbackup.RND'
    assert osbackup.exists
    log.info(f'Writing to legacy flight database: {osbackup}')

    orbitsse = Path(args.engineering) / 'ORBITSSE.RND'
    assert orbitsse.exists
    log.info(f'Reading from legacy engineering database: {orbitsse}')

    try:
        while True:
            update = \
                orbitv_file_interface.read_update_from_orbitsse(orbitsse)
            state = orbitx_connection.get_state([update])
            orbitv_file_interface.write_state_to_osbackup(state, osbackup)
            time.sleep(1)
    except grpc.RpcError as err:
        log.error(
            f'Got response code {err.code()} from orbitx, shutting down')


program = programs.Program(
    name=name,
    description=description,
    main=main,
    argparser=argument_parser,
    headless=True
)
