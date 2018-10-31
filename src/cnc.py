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
import os
import grpc

import cs493_pb2 as protos
import cs493_pb2_grpc as grpc_stubs
import common
import network
import physics


def main():
    state_server = network.StateServer()

    # Parse CLI arguments. Jupyter might add extra arguments, ignore them.
    parser = argparse.ArgumentParser()
    parser.add_argument('--port', type=int, default=common.DEFAULT_PORT)
    parser.add_argument('--flight-save', type=str,
                        default=common.DEFAULT_FLIGHT_SAVE_FILE)
    args, unknown = parser.parse_known_args()
    if unknown:
        print('Got unrecognized args,', unknown)
    # os.path.normpath deduplicates slashes and turns '/' into '\' on windows
    args.flight_save = os.path.normpath(args.flight_save)
    if not os.path.isabs(args.flight_save):
        # Take relative paths relative to the data/saves/
        args.flight_save = common.savefile(args.flight_save)

    print('Starting up physics engine,',
          f'loading save at {os.path.abspath(args.flight_save)}...')
    physics_engine = physics.PEngine(args.flight_save)

    print('Starting up networking...')
    server = grpc.server(concurrent.futures.ThreadPoolExecutor(max_workers=4))
    grpc_stubs.add_StateServerServicer_to_server(state_server, server)
    server.add_insecure_port(f'[::]:{args.port}')
    server.start()  # This doesn't block!
    print(f'Listening for RPC calls on port {args.port}. Ctrl-C exits.')

    try:
        for _ in range(0, 9001):
            next_tick_time = time.monotonic() + 1.0
            physics_engine.run_step(1)
            state_server.notify_state_change(
                physics_engine.state, physics_engine.state_lock)
            physics_engine.Save_json(common.AUTOSAVE_SAVEFILE)
            time_until_next_tick = next_tick_time - time.monotonic()
            time.sleep(time_until_next_tick)
    except KeyboardInterrupt:
        server.stop(0)
        print('Got Ctrl-C, exiting...')
    except:
        server.stop(0)
        raise


if __name__ == '__main__':
    main()
