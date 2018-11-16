"""Common code and class interfaces."""
import logging
import sys
import os.path

DEFAULT_LEAD_SERVER_HOST = 'localhost'
DEFAULT_LEAD_SERVER_PORT = 28430

DEFAULT_TIME_ACC = 1

CHEAT_FUEL = 0

# Set up a logger.
# Log DEBUG and higher to stderr,
# Log WARNING and higher to stdout.
logging.getLogger().setLevel(logging.DEBUG)
logging.captureWarnings(True)

formatter = logging.Formatter(
    '{asctime} {levelname} {module}.{funcName}: {message}',
    datefmt='%X',  # Just the time
    style='{')

# When changing output streams, consider that jupyter appmode, which is an easy
# way to give demos, will only show the stdout and not the stderr of a process.
handler = logging.StreamHandler(stream=sys.stdout)
handler.setLevel(logging.ERROR)
handler.setFormatter(formatter)
logging.getLogger().handlers = []
logging.getLogger().addHandler(handler)


def enable_verbose_logging():
    """Enables logging of all messages, from DEBUG upwards"""
    handler.setLevel(logging.DEBUG)


def savefile(name):
    return os.path.join(DATA_DIRECTORY, 'saves', name)


DATA_DIRECTORY = os.path.join(os.path.dirname(__file__), '..', 'data')
AUTOSAVE_SAVEFILE = savefile('autosave.json')
SOLAR_SYSTEM_SAVEFILE = savefile('OCESS.json')


class GrpcServerContext:
    """Context manager for a GRPC server."""

    def __init__(self, server):
        self._server = server

    def __enter__(self):
        pass

    def __exit__(self, *args):
        self._server.stop(0)
