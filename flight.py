#!/usr/bin/env python3

"""
Main for CnC, the 'Command and Control' server

This is the central server that stores all state, serves it to networked
modules, and receives updates from networked modules.
"""

import argparse
import copy
import logging
import os
import queue
import threading
import time
import warnings
import concurrent.futures
import urllib.parse

import grpc

import orbitx.orbitx_pb2_grpc as grpc_stubs
import orbitx.common as common
import orbitx.flight_gui as flight_gui
import orbitx.network as network
import orbitx.physics as physics

log = logging.getLogger()


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
                        default=('file:' + str(common.savefile('OCESS.json'))),
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

    parser.add_argument('--no-gui', action='store_true', default=False,
                        help='Don\'t launch the flight GUI.')

    parser.add_argument('-v', '--verbose', action='store_true', default=False,
                        help='Logs everything to stdout.')

    args, unknown = parser.parse_known_args()
    if unknown:
        log.warning(f'Got unrecognized args: {unknown}')

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
            args.data_location = args.data_location._replace(
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
            args.data_location = args.data_location._replace(netloc=(
                args.data_location.hostname +
                ':' +
                str(common.DEFAULT_LEAD_SERVER_PORT)
            ))

    if args.verbose:
        common.enable_verbose_logging()

    return args


def hacky_input_thread(cmd_queue):
    """This is hacky but works with jupyter notebook for the demo. Hi Colin!"""
    try:
        while True:
            cmd_queue.put(input((
                f'Time acceleration [default={common.DEFAULT_TIME_ACC}], '
                f'or planet centre [default=Habitat]'
                ':'
            )))
    except EOFError:
        # Program ending, let's pack it up.
        return


def lead_server_loop(args):
    """Main, 'while True'-style loop for a lead server. Blocking."""
    # Before you make changes to the lead server architecture, consider that
    # the GRPC server runs in a separate thread than this thread!
    state_server = network.StateServer()

    log.info(f'Loading save at {args.data_location.path}')
    physics_engine = physics.PEngine(
        common.load_savefile(args.data_location.path)
    )

    server = grpc.server(
        concurrent.futures.ThreadPoolExecutor(max_workers=4))
    grpc_stubs.add_StateServerServicer_to_server(state_server, server)
    server.add_insecure_port(f'[::]:{args.serve_on_port}')
    server.start()  # This doesn't block! We need a context manager from now on
    with common.GrpcServerContext(server):
        log.info(f'Server running on port {args.serve_on_port}. Ctrl-C exits.')

        cmd_queue = queue.Queue()
        input_thread = threading.Thread(
            target=hacky_input_thread, args=(cmd_queue,), daemon=True
        )
        input_thread.start()
        if not args.no_gui:
            gui = flight_gui.FlightGui(physics_engine.get_state())

        while True:
            state = physics_engine.get_state()
            state_server.notify_state_change(
                copy.deepcopy(state))
            # physics_engine.Save_json(common.AUTOSAVE_SAVEFILE)

            try:
                cmd = cmd_queue.get_nowait()
                if cmd.isdigit():
                    physics_engine.set_time_acceleration(float(cmd))
                else:
                    gui.recentre_camera(cmd)
            except queue.Empty:
                pass

            if not args.no_gui:
                gui.draw(state)
                gui.rate(common.FRAMERATE)
            else:
                time.sleep(common.TICK_TIME)


def mirroring_loop(args):
    """Main, 'while True'-style loop for a mirroring client. Blocking."""
    currently_mirroring = True

    log.info('Connecting to CnC server...')
    with network.StateClient(
        args.data_location.hostname, args.data_location.port
    ) as mirror_state:
        log.info(f'Querying lead server {args.data_location.geturl()}')
        state = mirror_state()
        physics_engine = physics.PEngine(state)

        if not args.no_gui:
            log.info('Initializing graphics (thanks sean)...')
            gui = flight_gui.FlightGui(state)

        while True:
            try:
                if currently_mirroring:
                    state = mirror_state()
                    physics_engine.set_state(state)
                else:
                    state = physics_engine.get_state()

                if not args.no_gui:
                    gui.draw(state)
                    gui.rate(common.FRAMERATE)
                else:
                    time.sleep(common.TICK_TIME)
            except KeyboardInterrupt:
                # TODO: hacky solution to turn off mirroring right now is a ^C
                if currently_mirroring:
                    currently_mirroring = False
                else:
                    raise


def main():
    """Delegate work to either lead_server_loop or mirroring_loop."""
    # vpython uses deprecated python features, but we shouldn't get a fatal
    # exception if we try to use vpython. DeprecationWarnings are normally
    # enabled when __name__ == __main__
    warnings.filterwarnings('once', category=DeprecationWarning)
    warnings.filterwarnings('once', category=ResourceWarning)

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
    except Exception:
        log.exception('Exception in main loop! Stopping execution.')
        raise


if __name__ == '__main__':
    main()
