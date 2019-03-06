#!/usr/bin/env python3

"""
main() for the compatibility server, an intermediary between orbitx and orbit.

Communicates to orbitx with GRPC, and to orbit using orbit_communication.py.

This script should be the only python code that uses orbitx.compat

General program flow:
- Get commandline arguments
- Parse sevpath.RND, allowing us to communicate to legacy QB clients
- Define a bunch of helpers
- Start reading and writing to orbit and orbitx
"""

import argparse
import asyncio
import signal
import warnings
import socket
from sys import version_info

from orbitx.compat import orbit_communication
from orbitx.compat import piloting_state


parser = argparse.ArgumentParser()
parser.add_argument("--sevpath", default="orbit-files/sevpath.RND",
                    help="Path to sevpath.RND")
parser.add_argument("--piloting", default="127.0.0.1:31415",
                    help="address:port of piloting client")
args = parser.parse_args()

orbit_communication.parse_sevpath(args.sevpath)
PILOTING_CLIENT = (args.piloting.split(':')[0],
                   int(args.piloting.split(':')[1]))


def update_orbit_files(event_loop):
    """Read, update all .RND files at 1 Hz. Helper for event loop."""
    reschedule_time = event_loop.time() + 1.0
    print('Updating orbit_files at', event_loop.time())
    orbit_communication.perform_qb_communication()
    event_loop.call_at(reschedule_time, update_orbit_files, event_loop)


status_message_delay = 1.0  # Seconds


def send_startup_message(event_loop):
    """Send startup message and schedule repeated updates with pilot client."""
    global status_message_delay
    global piloting
    piloting.startup_parse_starsr()
    print('Sending startup message at', event_loop.time())
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as startup_socket:
        startup_socket.connect(PILOTING_CLIENT)
        startup_socket.sendall(piloting.pack_immutables())
    reschedule_time = event_loop.time() + status_message_delay
    event_loop.call_at(reschedule_time, send_status_message, event_loop)


piloting_status_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
piloting_status_socket.connect(PILOTING_CLIENT)
piloting = piloting_state.Piloting(orbit_communication._client_path['flight'])


def send_status_message(event_loop):
    """Repeatedly update piloting client with current state."""
    global status_message_delay
    global piloting_status_socket
    global piloting
    piloting.parse_from_starsr()
    reschedule_time = event_loop.time() + status_message_delay
    print('Sending status update at', event_loop.time())
    piloting_status_socket.sendall(piloting.pack_mutables())
    event_loop.call_at(reschedule_time, send_status_message, event_loop)


def handle_exit(sig, _):
    """Ask event loop to finish all callbacks and exit."""
    if version_info >= (3, 5):
        # Only implemented >= python 3.5
        sig = signal.Signals(sig).name
    print("Got signal", sig, "and shutting down.")
    event_loop.stop()


for signame in [signal.SIGINT, signal.SIGTERM]:
    signal.signal(signame, handle_exit)


# Set up signal handler and asynchronous tasks.
event_loop = asyncio.get_event_loop()
event_loop.call_soon(update_orbit_files, event_loop)
event_loop.call_soon(send_startup_message, event_loop)

# Debug mode gives us useful information for development.
event_loop.set_debug(True)
warnings.simplefilter('always', ResourceWarning)

# Run until event_loop.stop() is called.
event_loop.run_forever()
event_loop.close()
piloting_status_socket.close()
