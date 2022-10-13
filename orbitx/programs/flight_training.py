import argparse
import atexit
import logging
import os
from pathlib import Path

from orbitx import common
from orbitx import physics
from orbitx import programs
from orbitx.physics.simulation import PhysicsEngine
from orbitx.graphics.flight import flight_gui
from orbitx.data_structures import savefile

log = logging.getLogger('orbitx')

name = "Flight Training"

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
        f'Name of the savefile to load, relative to {savefile.full_path(".")}. '
        'Should be a .json savefile written by OrbitX. '
        'Can also read OrbitV .RND savefiles.')
)


def main(args: argparse.Namespace):
    loadfile: Path
    if os.path.isabs(args.loadfile):
        loadfile = Path(args.loadfile)
    else:
        # Take paths relative to 'data/saves/'
        loadfile = savefile.full_path(args.loadfile)

    physics_engine = PhysicsEngine(savefile.load_savefile(loadfile))
    initial_state = physics_engine.get_state()

    gui = flight_gui.FlightGui(
        initial_state, title=name, running_as_mirror=False)
    atexit.register(gui.shutdown)

    if args.flamegraph:
        common.start_flamegraphing()
    if args.profile:
        common.start_profiling()

    while True:
        state = physics_engine.get_state()

        # If we have any commands, process them so the simthread has as
        # much time as possible to restart before next update.
        physics_engine.handle_requests(gui.pop_commands())

        gui.draw(state)
        gui.rate(common.FRAMERATE)


program = programs.Program(
    name=name,
    description=description,
    main=main,
    argparser=argument_parser
)
