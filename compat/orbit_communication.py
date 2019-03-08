"""Helper class to generalize logic of SERVERv.BAS file communication."""

from pathlib import Path, PurePath, PureWindowsPath
from typing import Dict, List

from compat import filetransforms

_client_path: Dict[str, Path] = {}
_file_vars: Dict[str, bytes] = {}
_file_connectors: List = []


def parse_sevpath(sevpath_path):
    """Parse sevpath.RND and set up module state."""
    global _client_path
    global _file_connectors
    # Read all paths to legacy clients from sevpath.RND
    clients = [
        "flight", "mirror", "telemetry", "simulator", "HABeecom", "MCeecom",
        "SIMeecom", "display", "HABeng", "SIMmirror", "HABdisplay"]
    with open(sevpath_path, "r") as sevpaths:
        for client in clients:
            _client_path[client] = (Path(sevpath_path).parent /
                                    PureWindowsPath(sevpaths.read(25).strip()))

    # Create helper classes for each legacy client.
    _file_connectors = [
        # Block 300
        FileConnector('simulator', ['HABeng'], 'ORB5res.RND', 412),
        # Block 400
        FileConnector('HABeecom', ['MCeecom', 'SIMeecom'],
                      'GASTELEMETRY.RND', 800),
        # Block 500
        FileConnector('MCeecom', ['HABeecom', 'SIMeecom'], 'GASMC.RND', 82),
        # Block 600
        FileConnector('SIMeecom', ['HABeecom'], 'GASSIM.RND', 182),
        # Block 700
        FileConnector('SIMeecom', ['HABeecom'], 'DOORSIM.RND', 276),
        # Block 800
        FileConnector('HABeng',
                      ['flight', 'telemetry', 'simulator', 'SIMmirror'],
                      'ORBITSSE.RND', 1159),
        # Block 900
        FileConnector('display', ['flight', 'mirror'], 'MST.RND', 26),
        # Block 930
        FileConnector('MCeecom', ['HABeecom', 'MCeecom'], 'TIME.RND', 26)
    ]


def _simplify_filename(filename):
    """Return the lowercase filename, no extensions."""
    return PurePath(filename.lower()).stem


class FileConnector:
    """Writes contents of src/filename to dest/filename.

    I noticed that serverv.bas does a lot of the following:
        read from path1/filename
        set global var based on file contents
        write to path2/filename

    This class seeks to generalize this logic.

    Call self.parsesrc to update 'global variables' (I know) in _file_vars
    based on the contents of src/filename and then
    call self.write_to_dest to write the contents for src/filename
    to dest/filename, with a predefined transformation.
    """

    def __init__(self, src, dests, filename, filesize):
        """Simply set up instance."""
        self._srcpath = _client_path[src] / filename
        self._destpaths = [_client_path[dest] / filename for dest in dests]
        self._filesize = filesize
        # Programmatically get parse, transform functions from filetransforms
        # e.g. _parsesrc = simulator_orb5res_parse
        self._parsesrc = getattr(
            filetransforms,
            src + '_' + _simplify_filename(filename) + '_parse')
        self._transform = getattr(
            filetransforms,
            src + '_' + _simplify_filename(filename) + '_transform')

    def process_src(self):
        """Read src/filename and possibly changes variables in _file_vars."""
        global _file_vars
        with self._srcpath.open('rb') as src:
            self._parsesrc(src, _file_vars)

    def write_to_dest(self):
        """Write src/filename to dest/filename with a transformation."""
        global _file_vars
        assert self._srcpath.stat().st_size == self._filesize
        with self._srcpath.open('rb') as src:
            file_contents = bytearray(src.read(self._filesize))
            assert file_contents[0] == file_contents[-1]
        precontents_len = len(file_contents)
        self._transform(file_contents, _file_vars)
        assert len(file_contents) == precontents_len
        for destpath in self._destpaths:
            with destpath.open('wb') as dest:
                dest.write(file_contents)
            assert destpath.stat().st_size == self._filesize


def perform_qb_communication():
    """Update all QB files with the proper logic."""
    global _file_connectors
    for connector in _file_connectors:
        connector.process_src()
    for connector in _file_connectors:
        connector.write_to_dest()
