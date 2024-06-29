"""
main() for Habitat Engineering, a program for control of Habitat and AYSE
subsystems, electrical power distribution, and thermal loading.

Communicates to orbitx with GRPC.
"""

import argparse
import logging
from typing import List

import grpc
import sv_ttk

from orbitx import network
from orbitx.common import Program, Request
from orbitx.graphics.compat_gui import StartupFailedGui
from orbitx.graphics.eng.main_window import MainApplication


log = logging.getLogger('orbitx')


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

_commands_to_send: List[Request] = []


def main(args: argparse.Namespace):
    log.info(f'Connecting to OrbitX Physics Server: {args.physics_server}')

    try:
        # Make sure we have a connection before continuing.
        orbitx_connection = network.NetworkedStateClient(
            Request.HAB_ENG, args.physics_server)
    except grpc.RpcError as err:
        log.error(f'Could not connect to Physics Server: {err.code()}')
        StartupFailedGui(args.physics_server, err)
        return

    gui = MainApplication()

    def network_task():
        user_commands = pop_commands()
        if user_commands:
            log.info(f'Hab eng sending commands: {user_commands}')
        state = orbitx_connection.get_state(user_commands)
        gui.redraw(state)
        gui.after(int(1000), network_task)

    network_task()
    # sv_ttk.set_theme('light')
    gui.mainloop()


def push_command(command: Request) -> None:
    global _commands_to_send
    _commands_to_send.append(command)


def pop_commands() -> List[Request]:
    global _commands_to_send
    commands = _commands_to_send
    _commands_to_send = []
    return commands


program = Program(
    name=name,
    description=description,
    main=main,
    argparser=argument_parser
)
