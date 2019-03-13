#!/usr/bin/env python3

"""
main() for the compatibility server, an intermediary between orbitx and orbit.

Communicates to orbitx with GRPC, and to orbit using orbit_communication.py.

This script should be the only python code that uses the compat module

General program flow:
- Get commandline arguments
- Parse sevpath.RND, allowing us to communicate to legacy QB clients
- Define a bunch of helpers
- Start reading and writing to orbit and orbitx
"""

import argparse
import time
from pathlib import Path

import grpc

from orbitx import common
from orbitx import network
from orbitx.compat import orbit_file_interface

parser = argparse.ArgumentParser()
parser.add_argument("--engineering", default="orbit-files/",
                    help=(
                        "Path to engineering, "
                        "containing OSbackup.RND and ORBITSSE.RND"
                    ))
parser.add_argument("--piloting", default=(
    f"{common.DEFAULT_LEAD_SERVER_HOST}:{common.DEFAULT_LEAD_SERVER_PORT}"),
    help="address:port of piloting client")
args = parser.parse_args()

with network.StateClient(*args.piloting.split(':')) as orbitx_connection:
    assert Path(args.engineering).exists

    osbackup = Path(args.engineering) / 'OSbackup.RND'
    assert osbackup.exists
    print(f'Writing to legacy flight database: {osbackup}')

    orbitsse = Path(args.engineering) / 'ORBITSSE.RND'
    assert orbitsse.exists
    print(f'Reading from legacy engineering database: {orbitsse}')

    try:
        while True:
            update = orbit_file_interface.read_update_from_orbitsse(orbitsse)
            state = orbitx_connection(update)
            orbit_file_interface.write_state_to_osbackup(state, osbackup)
            time.sleep(1)
    except grpc.RpcError as err:
        print(f'Got response code {err.code()} from orbitx, shutting down')
