"""
main() for the compatibility server, an intermediary between orbitx and orbit.

Communicates to orbitx with GRPC, and to orbit using orbit_communication.py.
"""

import argparse
import logging
import time
from pathlib import Path

import grpc

from orbitx import common
from orbitx import network
from orbitx import orbitv_file_interface

log = logging.getLogger()


description = 'Compat description'

argument_parser = argparse.ArgumentParser('compat', description=description)
argument_parser.add_argument(
    "--engineering", default="orbit-files/",
    help=(
        "Path to engineering, "
        "containing OSbackup.RND and ORBITSSE.RND")
)
argument_parser.add_argument("--piloting", default=(
    f"{common.DEFAULT_LEAD_SERVER_HOST}:{common.DEFAULT_LEAD_SERVER_PORT}"),
    help="address:port of piloting client")


def main(args: argparse.Namespace):
    orbitx_connection = network.StateClient(*args.piloting.split(':'))
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
            state = orbitx_connection.get_state(update)
            orbitv_file_interface.write_state_to_osbackup(state, osbackup)
            time.sleep(1)
    except grpc.RpcError as err:
        log.info(
            f'Got response code {err.code()} from orbitx, shutting down')


Compat = common.Program(
    name='Compat',
    description=description,
    main=main,
    argparser=argument_parser
)
