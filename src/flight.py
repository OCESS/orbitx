#!/usr/bin/env python3

"""
Main for the flight module, used by astronauts to pilot the habitat.

This runs a GUI for astronauts to interface with, and will send and receive
updates from the central server.
"""

import argparse
import time
import threading

import grpc
import vpython

import cs493_pb2 as protos
import cs493_pb2_grpc as grpc_stubs
import constants

state_lock = threading.Lock()
physical_state = protos.PhysicalState()

class Graphics:
    def __init__(self, texture_path='textures/'):
        self.scene = vpython.canvas(
            title='Space Simulator',
            align='left',
            width=600,
            height=600,
            center=vpython.vector(0,0,0)
        )

        self.spheres = []
        self.first_draw = True

    def draw(self):
        global state_lock
        with state_lock:
            for planet in physical_state.entities:
                if self.first_draw:
                    self.spheres.append(self._draw_sphere(planet))
                    self.first_draw = False
                else:
                    self._update_sphere(self.spheres[0], planet) # TODO: hack

    def _draw_sphere(self, planet):
        return vpython.sphere(
            pos=vpython.vector(planet.x, 0, planet.y),
            radius=planet.r,
            make_trail=True
        )

    def _update_sphere(self, sphere, planet):
        sphere.pos = vpython.vector(planet.x, planet.y, 0)


class Networking:
    """
    Context manager for networking.

    Should return a function that evaluates to the state of the entities.
    This will let us change the implementation of this class without changing
    calling code.

    Usage:
        with Networking('localhost', 28430) as physical_state_getter:
            while True:
                sleep(1)
                physical_state = physical_state_getter()
    """
    def __init__(self, cnc_address, cnc_port):
        self.cnc_location = f'{cnc_address}:{cnc_port}'

    def _get_physical_state(self):
        return self.stub.get_physical_state(
            protos.ClientId(ident=protos.ClientId.FLIGHT))

    def __enter__(self):
        self.channel = grpc.insecure_channel(self.cnc_location)
        self.stub = grpc_stubs.StateSyncherStub(self.channel)
        return self._get_physical_state

    def __exit__(self, *args):
        self.channel.close()

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--cnc-address', type=str, default=constants.DEFAULT_CNC_ADDRESS)
    parser.add_argument('--cnc-port', type=int, default=constants.DEFAULT_PORT)
    args = parser.parse_args()

    print('Initializing graphics (thanks sean)...')
    graphics = Graphics()

    print('Connecting to CnC server...')
    with Networking(args.cnc_address, args.cnc_port) as physical_state_getter:
        print('Connected.')
        try:
            while True:
                print('Getting update from CnC server...')
                physical_state_copy = physical_state_getter()
                with state_lock:
                    global physical_state
                    physical_state = physical_state_copy
                graphics.draw()
                time.sleep(1)
        except KeyboardInterrupt:
            pass

if __name__ == '__main__':
    main()
