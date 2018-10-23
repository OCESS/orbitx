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
import common
import network

state_lock = threading.Lock()
physical_state = protos.PhysicalState()

def generate_entities():
    "Quick function to fill up some entities, before Ye Qin gets physics in"
    import random
    global physical_state
    global state_lock
    with state_lock:
        if not physical_state.entities:
            physical_state.entities.add()
        physical_state.timestamp = time.monotonic()
        physical_state.entities[0].name = 'Earth'
        physical_state.entities[0].x = random.uniform(-60, 60)
        physical_state.entities[0].y = random.uniform(-60, 60)
        physical_state.entities[0].vx = random.uniform(-30, 30)
        physical_state.entities[0].vy = random.uniform(-30, 30)
        physical_state.entities[0].r = random.uniform(20, 30)
        physical_state.entities[0].mass = random.uniform(-30, 30)

def main():
    global state_lock
    state_server = network.StateServer()

    parser = argparse.ArgumentParser()
    parser.add_argument('--port', type=int, default=common.DEFAULT_PORT)
    args = parser.parse_args()

    print('Starting CnC server...')
    server = grpc.server(concurrent.futures.ThreadPoolExecutor(max_workers=4))
    grpc_stubs.add_StateServerServicer_to_server(state_server, server)
    server.add_insecure_port(f'[::]:{args.port}')
    server.start() # This doesn't block!
    print(f'Listening for RPC calls on port {args.port}. Ctrl-C exits.')

    try:
        while True:
            generate_entities()
            state_server.notify_state_change(physical_state, state_lock)
            time.sleep(1)
    except KeyboardInterrupt:
        server.stop(0)

if __name__ == '__main__':
    main()
