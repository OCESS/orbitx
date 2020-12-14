"""
main() for Habitat Engineering, a program for control of Habitat and AYSE
subsystems, electrical power distribution, and thermal loading.

Communicates to orbitx with GRPC.
"""

import argparse
import logging

import grpc

from orbitx import network
from orbitx import programs
from orbitx.graphics.compat_gui import StartupFailedGui
from orbitx.graphics.eng_gui import MainApplication
from orbitx.strings import HABITAT


log = logging.getLogger()


name = "Habitat Engineering"

description = (
    "Control Habitat and AYSE subsystems, electrical power distribution, and"
    "thermal loading."
)

argument_parser = argparse.ArgumentParser(
    'habeng', description=description.replace('<br />', '\n'))
argument_parser.add_argument(
    "--physics-server", default="localhost",
    help=(
        'Network name of the computer where the physics server is running. If '
        'the physics server is running on the same machine, put "localhost".')
)


def main(args: argparse.Namespace):
    log.info(f'Connecting to OrbitX Physics Server: {args.physics_server}')

    try:
        # Make sure we have a connection before continuing.
        orbitx_connection = network.NetworkedStateClient(
            network.Request.HAB_ENG, args.physics_server)
    except grpc.RpcError as err:
        log.error(f'Could not connect to Physics Server: {err.code()}')
        StartupFailedGui(args.physics_server, err)
        return

    gui = MainApplication()

    def network_task():
        gui.contrived_keybind_function()
        user_commands = gui.pop_commands()
        state = orbitx_connection.get_state(user_commands)
        gui.update_labels(state[HABITAT].pos[0])
        print('R-CON1 is connected?', state.engineering.components['R-CON1'].connected)
        gui.after(int(1000), network_task)

    network_task()
    gui.mainloop()


program = programs.Program(
    name=name,
    description=description,
    main=main,
    argparser=argument_parser
)
