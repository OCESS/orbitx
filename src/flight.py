#!/usr/bin/env python3

"""
Main for CnC, the 'Command and Control' server

This is the central server that stores all state, serves it to networked
modules, and receives updates from networked modules.
"""

import argparse
import concurrent.futures
import time
import os
import grpc
import urllib.parse
import copy

import cs493_pb2_grpc as grpc_stubs
import common
import network
import physics
import flight_gui


def parse_args():
    """Parse CLI arguments. Jupyter might add extra arguments, ignore them."""
    parser = argparse.ArgumentParser(
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description=(
            'This program can be started in either "lead server" mode\n'
            'or "mirror" mode.\n'
            '\n'
            'In "lead server" mode, this program simulates a solar system\n'
            'using the flight data from the JSON savefile specified as a\n'
            'command-line argument to this program. This program will also\n'
            'serve physics data on the port specified by --serve-on-port.\n'
            'To activate "lead server" mode, pass "file:path/to/file" or\n'
            '"file:/absolute/path/to/file" as the data_location argument.\n'
            '\n'
            'In "mirror" mode, this program requests physics updates from\n'
            'the lead server specified by the hostname and optional port\n'
            'argument.\n'
            'To activate "mirror" mode, pass "mirror://..." as the\n'
            'data_location argument.'
        ))

    parser.add_argument('data_location', type=str, nargs='?',
                        default=('file:' + common.SOLAR_SYSTEM_SAVEFILE),
                        help=(
                            'Where flight data is located. Accepts arguments'
                            ' of the form '
                            '"mirror://hostname" or "mirror://hostname:port" '
                            'or "file:path/to/save.json" or '
                            '"file:/absolute/path/to/save.json". '
                            'See help text for details. Defaults to '
                            'file:../data/saves/OCESS.json.'
                        ))

    parser.add_argument('--serve-on-port', type=int, metavar='PORT',
                        help=(
                            'For a lead server, specifies which port to serve '
                            'physics data on. Specifying this for a mirror is '
                            ' an error.'
                        ))

    parser.add_argument('--flight-gui', action='store_true', default=False,
                        help=(
                            'Launches a flight GUI.'
                        ))

    args, unknown = parser.parse_known_args()
    if unknown:
        print('Got unrecognized args,', unknown)

    args.data_location = urllib.parse.urlparse(args.data_location)
    # Check that the data_location is well-formed
    assert args.data_location.scheme == 'file' or \
        args.data_location.scheme == 'mirror'

    if args.data_location.scheme == 'file':
        # We're in lead server mode
        assert not args.data_location.netloc
        assert args.data_location.path
        assert not args.data_location.query
        assert not args.data_location.fragment
        if not os.path.isabs(args.data_location.path):
            # Take relative paths relative to the data/saves/
            args.data_location._replace(
                path=common.savefile(args.data_location.path)
            )
        if args.serve_on_port is None:
            # We can't have a default value of this port, because we want to
            # check for its existence when we're in mirroring client mode
            args.serve_on_port = common.DEFAULT_LEAD_SERVER_PORT
    else:
        # We're in mirroring client mode
        assert args.serve_on_port is None  # Meaningless in this mode
        assert args.data_location.netloc
        assert not args.data_location.path
        assert not args.data_location.query
        assert not args.data_location.fragment
        if not args.data_location.port:
            # Port is optional. If it does not exist use the default port.
            args.data_location._replace(netloc=(
                args.data_location.hostname +
                ':' +
                str(common.DEFAULT_LEAD_SERVER_PORT)
            ))

    return args


def lead_server_loop(args):
    """Main, 'while True'-style loop for a lead server. Blocking."""
    # Before you make changes to the lead server architecture, consider that
    # the GRPC server runs in a separate thread than this thread!
    state_server = network.StateServer()

    print(f'Starting up physics, loading save at {args.data_location.path}')
    physics_engine = physics.PEngine(flight_savefile=args.data_location.path)

    print('Starting up lead server networking...')
    server = grpc.server(
        concurrent.futures.ThreadPoolExecutor(max_workers=4))
    grpc_stubs.add_StateServerServicer_to_server(state_server, server)
    server.add_insecure_port(f'[::]:{args.serve_on_port}')
    server.start()  # This doesn't block! We need a context manager from now on
    with common.GrpcServerContext(server):
        print(f'Server running on port {args.serve_on_port}. Ctrl-C exits.')

        if args.flight_gui:
            print('Initializing graphics (thanks sean)...')
            gui = flight_gui.FlightGui(physics_engine.state)

        next_tick_time = time.monotonic() + 1.0

        for _ in range(0, 9001):
            physics_engine.run_step(100000)
            state_server.notify_state_change(
                copy.deepcopy(physics_engine.state))
            physics_engine.Save_json(common.AUTOSAVE_SAVEFILE)

            if args.flight_gui:
                gui.draw(physics_engine.state)
                gui.wait(1)
            else:
                time_until_next_tick = next_tick_time - time.monotonic()
                time.sleep(time_until_next_tick)
                next_tick_time = time.monotonic() + 1.0


def mirroring_loop(args):
    """Main, 'while True'-style loop for a mirroring client. Blocking."""
    currently_mirroring = True

    print('Connecting to CnC server...')
    with network.StateClient(
        args.data_location.hostname, args.data_location.port
    ) as mirror_state:
        print(f'Getting physics engine state [{args.data_location.geturl()}]')
        physics_engine = physics.PEngine(mirror_state=mirror_state)

        if args.flight_gui:
            print('Initializing graphics (thanks sean)...')
            gui = flight_gui.FlightGui(mirror_state())

        next_tick_time = time.monotonic() + 1.0

        for _ in range(0, 9001):
            try:
                if currently_mirroring:
                    physics_engine.set_state(mirror_state())
                else:
                    physics_engine.run_step(1)

                if args.flight_gui:
                    gui.draw(physics_engine.state)
                    gui.wait(1)
                else:
                    time_until_next_tick = next_tick_time - time.monotonic()
                    time.sleep(time_until_next_tick)
                    next_tick_time = time.monotonic() + 1.0
            except KeyboardInterrupt:
                # TODO: hacky solution to turn off mirroring right now is a ^C
                if currently_mirroring:
                    currently_mirroring = False
                else:
                    raise


def main():
    """Delegate work to either lead_server_loop or mirroring_loop."""
    args = parse_args()
    try:
        if args.data_location.scheme == 'file':
            lead_server_loop(args)
        else:
            assert args.data_location.scheme == 'mirror'
            mirroring_loop(args)
    except KeyboardInterrupt:
        # We're expecting ctrl-C will end the program, hide the exception from
        # the user.
        pass


if __name__ == '__main__':
    main()
