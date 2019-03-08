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

from orbitx import common
from compat import orbit_file_interface
from orbitx import network

parser = argparse.ArgumentParser()
parser.add_argument("--osbackup", default="orbit-files/OSbackup.RND",
                    help="Path to OSbackup.RND")
parser.add_argument("--piloting", default=(
    f"{common.DEFAULT_LEAD_SERVER_HOST}:{common.DEFAULT_LEAD_SERVER_PORT}"),
    help="address:port of piloting client")
args = parser.parse_args()

args.osbackup = Path(args.osbackup)
assert args.osbackup.name == 'OSbackup.RND'
assert args.osbackup.exists


with network.StateClient(*args.piloting.split(':')) as piloting_server:
    while True:
        state = piloting_server()
        print(f'Got state at t={state.timestamp}')
        orbit_file_interface.write_state_to_osbackup(state, args.osbackup)
        time.sleep(1)
