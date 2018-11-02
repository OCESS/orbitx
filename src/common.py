"""Common code and class interfaces."""
import os.path

DEFAULT_LEAD_SERVER_HOST = 'localhost'
DEFAULT_LEAD_SERVER_PORT = 28430


def savefile(name):
    return os.path.join(SAVE_DIRECTORY, name)


SAVE_DIRECTORY = os.path.join(os.path.dirname(__file__), '..', 'data', 'saves')
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
