import argparse
import atexit
import logging
import os
from pathlib import Path

from orbitx import common
from orbitx import network
from orbitx import physics
from orbitx import programs
from orbitx.graphics import flight_gui

log = logging.getLogger()


name = "Flight Training Program"

description = (
    "This standalone program gives you piloting control of the "
    "Habitat, as it simulates the Habitat in spaceflight."
)

argument_parser = argparse.ArgumentParser(
    'flighttraining',
    description=description.replace('<br />', '\n'))
argument_parser.add_argument(
    'loadfile', type=str, nargs='?', default='OCESS.json',
    help=(
        'Name of the savefile to be loaded. Should be a .json'
        ' file, in a format that OrbitX expects.')
)


def main(args: argparse.Namespace):
    loadfile: Path
    if os.path.isabs(args.loadfile):
        loadfile = Path(args.loadfile)
    else:
        # Take paths relative to 'data/saves/'
        loadfile = common.savefile(args.loadfile)

    log.info(f'Loading save at {loadfile}')
    physics_engine = physics.PEngine(common.load_savefile(loadfile))
    initial_state = physics_engine.get_state()

    gui = flight_gui.FlightGui(initial_state, running_as_mirror=False)
    atexit.register(gui.shutdown)

    if args.profile:
        common.start_profiling()

    while True:
        state = physics_engine.get_state()
        user_commands = gui.pop_commands()

        # If we have any commands, process them so the simthread has as
        # much time as possible to restart before next update.
        for command in user_commands:
            if command.ident == network.Request.NOOP:
                continue
            log.info(f'Got command: {command}')
            physics_engine.handle_request(command)

        gui.draw(state)
        gui.rate(common.FRAMERATE)


program = programs.Program(
    name=name,
    description=description,
    main=main,
    argparser=argument_parser,
    headless=False
)
