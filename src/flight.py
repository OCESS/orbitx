#!/usr/bin/env python3

"""
Main for the flight module, used by astronauts to pilot the habitat.

This runs a GUI for astronauts to interface with, and will send and receive
updates from the central server.
"""

import argparse
import time
import threading

import cs493_pb2 as protos
import cs493_pb2_grpc as grpc_stubs
import common
import flight_gui
import network

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--cnc-address', type=str, default=common.DEFAULT_CNC_ADDRESS)
    parser.add_argument('--cnc-port', type=int, default=common.DEFAULT_PORT)
    args = parser.parse_args()

    print('Connecting to CnC server...')
    with network.StateClient(args.cnc_address, args.cnc_port) as physical_state_getter:
        print('Initializing graphics (thanks sean)...')
        gui = flight_gui.FlightGui(physical_state_getter)
        print('Connected.')
        try:
            while True:
                print('Getting update from CnC server...')
                gui.draw(physical_state_getter())
                gui.wait(1)
        except KeyboardInterrupt:
            pass

if __name__ == '__main__':
    main()
