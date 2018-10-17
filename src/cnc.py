#!/usr/bin/env python3

"""
Main for CnC, the 'Command and Control' server

This is the central server that stores all state, serves it to networked
modules, and receives updates from networked modules.
"""

import argparse
import threading
import concurrent.futures
import time

import grpc

import cs493_pb2 as protos
import cs493_pb2_grpc as grpc_stubs
import constants as constants

state_lock = threading.Lock()
physical_state = protos.PhysicalState()

class StateSyncher(grpc_stubs.StateSyncherServicer):
    """
    Service for sending state to clients.
    """

    def get_physical_state(self, request, context):
        """
        Server-side implementation of this remote procedure call (RPC).

        Usage: A client will call "GetPhysicalState", which will fire off a
        request to this server. The below function implementation will return a
        value and that value will be sent over the network to the client, and
        the client's call of "GetPhysicalState" will return whatever value we
        produce here.

        Magic!
        """
        with state_lock:
            self.local_physical_state = physical_state
        return self.local_physical_state

def generate_entities():
    "Quick function to fill up some entities, before Ye Qin gets physics in"
    import random
    global physical_state
    with state_lock:
        if not physical_state.entities:
            physical_state.entities.add()
        physical_state.timestamp = time.monotonic()
        physical_state.entities[0].x = random.uniform(-1e300, 1e300)
        physical_state.entities[0].y = random.uniform(-1e300, 1e300)
        physical_state.entities[0].vx = random.uniform(-1e300, 1e300)
        physical_state.entities[0].vy = random.uniform(-1e300, 1e300)
        physical_state.entities[0].r = random.uniform(-1e300, 1e300)
        physical_state.entities[0].mass = random.uniform(-1e300, 1e300)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--port', type=int, default=constants.DEFAULT_PORT)
    args = parser.parse_args()

    print('Starting CnC server...')
    server = grpc.server(concurrent.futures.ThreadPoolExecutor(max_workers=4))
    grpc_stubs.add_StateSyncherServicer_to_server(StateSyncher(), server)
    server.add_insecure_port(f'[::]:{args.port}')
    server.start() # This doesn't block!
    print(f'Listening for RPC calls on port {args.port}. Ctrl-C exits.')

    try:
        while True:
            generate_entities()
            time.sleep(1)
    except KeyboardInterrupt:
        server.stop(0)

if __name__ == '__main__':
    main()
