"""
Functions for interpreting a .json dump of orbitx.proto:PhysicsState into a
PhysicsState that can be accessed by other python code, and vice versa.
"""
from __future__ import annotations

import logging
import sys
import json
from pathlib import Path

import google.protobuf.json_format

from orbitx import common
from orbitx import strings
from orbitx.data_structures.space import PhysicsState
from orbitx.physics import electroconstants

import orbitx.orbitx_pb2 as protos

log = logging.getLogger('orbitx')


PROGRAM_PATH: Path

if getattr(sys, 'frozen', False):
    # We're running from a PyInstaller exe, use the path of the exe
    PROGRAM_PATH = Path(sys.executable).parent
elif sys.path[0] == '':
    # We're running from a Python REPL. For information on what sys.path[0]
    # means, read https://docs.python.org/3/library/sys.html#sys.path
    # note path[0] == '' means Python is running as an interpreter.
    PROGRAM_PATH = Path.cwd()
else:
    PROGRAM_PATH = Path(sys.path[0])


def full_path(name: str) -> Path:
    """
    Given just the name of a savefile, returns a full Path representation.

    Example:
    savefile('OCESS.json') -> /path/to/orbitx/data/saves/OCESS.json
    """
    return PROGRAM_PATH / 'data' / 'saves' / name


def load_savefile(file: Path) -> PhysicsState:
    """
    Loads the physics state represented by the input file.
    If the input file is an OrbitX-style .json file, simply loads it.
    If the input file is an OrbitV-style .rnd file, tries to interpret it
    and also loads the adjacent STARSr file to produce a PhysicsState.
    """

    physics_state: PhysicsState
    log.info(f'Loading savefile {file.resolve()}')

    assert isinstance(file, Path)
    if file.suffix.lower() == '.rnd':
        from orbitx import orbitv_file_interface
        physics_state = \
            orbitv_file_interface.clone_orbitv_state(file)

    else:
        if file.suffix.lower() != '.json':
            log.warning(
                f'{file} is not a .json file, trying to load it anyways.')

        with open(file, 'r') as f:
            json_dict = json.load(f)

        for component_i, component in enumerate(json_dict['engineering']['components']):
            if 'name' in component:
                # This is just an informational field we add in while saving, get rid of it.
                del component['name']
            if 'temperature' not in component:
                # Default for this field should be the resting temperature, not zero.
                component['temperature'] = electroconstants.RESTING_TEMPERATURE[component_i]

        read_state = protos.PhysicalState()
        google.protobuf.json_format.ParseDict(json_dict, read_state)

        if len(read_state.engineering.components) < common.N_COMPONENTS:
            # We allow savefiles to not specify any components.
            # If we see this, create a list of empty components in the protobuf before parsing it.
            for i in range(len(read_state.engineering.components), common.N_COMPONENTS):
                read_state.engineering.components.append(
                    protos.EngineeringState.Component(
                        temperature=electroconstants.RESTING_TEMPERATURE[i]
                    )
                )

        physics_state = PhysicsState(None, read_state)

    if physics_state.timestamp == 0:
        physics_state.timestamp = common.DEFAULT_INITIAL_TIMESTAMP
    if physics_state.time_acc == 0:
        physics_state.time_acc = common.DEFAULT_TIME_ACC.value
    if physics_state.reference == '':
        physics_state.reference = common.DEFAULT_REFERENCE
    if physics_state.target == '':
        physics_state.target = common.DEFAULT_TARGET
    if physics_state.srb_time == 0:
        physics_state.srb_time = common.SRB_FULL

    return physics_state


def write_savefile(state: PhysicsState, file: Path):
    """Writes state to the specified savefile path (use savefile() to get
    a savefile path in data/saves/). Returns a possibly-different path that it
    was saved under.
    Does some post-processing, like adding descriptive names to components."""
    if file.suffix.lower() != '.json':
        # Ensure a .json suffix.
        file = file.parent / (file.name + '.json')
    log.info(f'Saving to savefile {file.resolve()}')

    savefile_json_dict = google.protobuf.json_format.MessageToDict(
        state.as_proto(),
        including_default_value_fields=False,
        preserving_proto_field_name=True,
        use_integers_for_enums=False,
    )

    for i, component in enumerate(savefile_json_dict['engineering']['components']):
        component['name'] = strings.COMPONENT_NAMES[i]

    with open(file, 'w') as outfile:
        json.dump(savefile_json_dict, outfile, indent=2)

    return file


# To upgrade savefiles, you can run the following command:
# python -c 'from orbitx.data_structures.savefile import upgrade_savefile; from pathlib import Path; upgrade_savefile(Path(\"data/saves/tests/engineering-test.json\"))'
# Change the path to anything you want.
def upgrade_savefile(file: Path):
    """Take a savefile, parse it, and write it back out again.
    Use this if e.g. an older version of orbitx wrote the savefile, and you want
    to upgrade the savefile."""
    physics_state = load_savefile(file)
    write_savefile(physics_state, file)
