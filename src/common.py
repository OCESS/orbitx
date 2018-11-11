"""Common code and class interfaces."""
import logging
import os.path

DEFAULT_LEAD_SERVER_HOST = 'localhost'
DEFAULT_LEAD_SERVER_PORT = 28430

TICK_LENGTH = 0.01
TICK_RATE = round(1 / TICK_LENGTH)


logging.basicConfig(
    level=logging.DEBUG,
    datefmt='%X',  # Just the time
    style='{',
    format='{asctime} {levelname} {module}:{funcName} L{lineno}: {message}'
)


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
