#!/usr/bin/env python3

"""
Main for CnC, the 'Command and Control' server

This is the central server that stores all state, serves it to networked
modules, and receives updates from networked modules.
"""

import argparse
import atexit
import logging
import sys
import warnings
from pathlib import Path

from orbitx import common
from orbitx.variants import compat, lead, mirror

log = logging.getLogger()


def log_git_info():
    """For ease in debugging, try to get some version information.
    This should never throw a fatal error, it's just nice-to-know stuff."""
    try:
        git_dir = Path('.git')
        head_file = git_dir / 'HEAD'
        with head_file.open() as f:
            head_contents = f.readline().strip()
            log.info(f'Contents of .git/HEAD: {head_contents}')
        if head_contents.split()[0] == 'ref:':
            hash_file = git_dir / head_contents.split()[1]
            with hash_file.open() as f:
                log.info(f'Current reference hash: {f.readline().strip()}')
    except FileNotFoundError:
        return


def main():
    """Delegate work to one of the OrbitX programs."""

    # vpython uses deprecated python features, but we shouldn't get a fatal
    # exception if we try to use vpython. DeprecationWarnings are normally
    # enabled when __name__ == __main__
    warnings.filterwarnings('once', category=DeprecationWarning)
    # vpython generates other warnings, as well as its use of asyncio
    warnings.filterwarnings('ignore', category=ResourceWarning)
    warnings.filterwarnings('ignore', module='vpython|asyncio|autobahn')

    log_git_info()

    parser = argparse.ArgumentParser(prog='orbitx')
    parser.add_argument('-v', '--verbose', action='store_true', default=False,
                        help='Logs everything to both logfile and output.')

    parser.add_argument('--profile', action='store_true', default=False,
                        help='Generating profiling reports, for a flamegraph.')

    # Use the argument parsers that each variant defines
    subparsers = parser.add_subparsers(help='Which OrbitX variant to run')
    lead_subparser = subparsers.add_parser(
        'lead', help='Lead flight server', add_help=False,
        parents=[lead.argument_parser])
    lead_subparser.set_defaults(main_loop=lead.main)

    mirror_subparser = subparsers.add_parser(
        'mirror', help='Mirror a lead flight server', add_help=False,
        parents=[mirror.argument_parser])
    mirror_subparser.set_defaults(main_loop=mirror.main)

    compat_subparser = subparsers.add_parser(
        'compat', help='Compatibility layer for OrbitV', add_help=False,
        parents=[compat.argument_parser])
    compat_subparser.set_defaults(main_loop=compat.main)

    args = parser.parse_args()

    if args.verbose:
        common.enable_verbose_logging()

    try:
        args.main_loop(args)
    except KeyboardInterrupt:
        # We're expecting ctrl-C will end the program, hide the exception from
        # the user.
        pass
    except Exception as e:
        log.exception('Unexpected exception, exiting...')
        atexit.unregister(common.print_handler_cleanup)

        if isinstance(e, (AttributeError, ValueError)):
            proto_file = Path('orbitx', 'orbitx.proto')
            generated_file = Path('orbitx', 'orbitx_pb2.py')
            if not generated_file.is_file():
                log.warning('================================================')
                log.warning(f'{proto_file} does not exist.')
            elif proto_file.stat().st_mtime > generated_file.stat().st_mtime:
                log.warning('================================================')
                log.warning(f'{proto_file} is newer than {generated_file}.')
            else:
                # We thought that generated protobuf definitions were out of
                # date, but it doesn't actually look like that's the case.
                # Raise the exception normally.
                raise

            log.warning('A likely fix for this fatal exception is to run the')
            log.warning('`build` target of orbitx/Makefile, or at least')
            log.warning('copy-pasting the contents of the `build` target and')
            log.warning('running it in your shell.')
            log.warning('You\'ll have to do this every time you change')
            log.warning(str(proto_file))
            log.warning('================================================')

        raise


if __name__ == '__main__':
    main()
