"""Common code and class interfaces."""
import logging
import sys
import os.path

DEFAULT_LEAD_SERVER_HOST = 'localhost'
DEFAULT_LEAD_SERVER_PORT = 28430

TICK_LENGTH = 0.01
TICK_RATE = round(1 / TICK_LENGTH)

DEFAULT_TIME_ACC = 1


# Set up a logger.
# Log DEBUG and higher to stderr,
# Log WARNING and higher to stdout.
logging.getLogger().setLevel(logging.DEBUG)

formatter = logging.Formatter(
    '{asctime} {levelname} {module}.{funcName}: {message}',
    datefmt='%X',  # Just the time
    style='{')

debug_handler = logging.StreamHandler(stream=sys.stderr)
debug_handler.setLevel(logging.DEBUG)
debug_handler.setFormatter(formatter)
logging.getLogger().addHandler(debug_handler)

important_handler = logging.StreamHandler(stream=sys.stdout)
important_handler.setLevel(logging.ERROR)
important_handler.setFormatter(formatter)
logging.getLogger().addHandler(important_handler)


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
