"""A simple textual GUI for the Physics Server."""

import socket
import logging
from pathlib import Path
from typing import List, Optional

from grpc._cython import cygrpc
from google.protobuf import json_format
from grpc_channelz.v1 import channelz_pb2
import vpython

from orbitx import common

log = logging.getLogger()


class ConnectionViewer:
    """Queries C-Core channelz statistics to see what clients have open channels
    with this GRPC process."""
    def __init__(self):
        self._target_server_id: Optional[int] = None

    def connected_clients(self) -> List[str]:
        """Returns a list of unique address:port identifiers, each
        corresponding to a connected client."""
        if self._target_server_id is None:
            # Get the server id of the only existing server in this process.
            servers = json_format.Parse(
                cygrpc.channelz_get_servers(0),
                channelz_pb2.GetServersResponse(),
            )
            assert len(servers.server) == 1
            self._target_server_id = servers.server[0].ref.server_id

        # Get all server sockets, each of which represent a client connection.
        ssockets = json_format.Parse(
            cygrpc.channelz_get_server_sockets(
                self._target_server_id, 0, 0),
            channelz_pb2.GetServerSocketsResponse(),
        )
        return [ssock.name for ssock in ssockets.socket_ref]


class ServerGui:
    UPDATES_PER_SECOND = 10

    def __init__(self):
        self.connection_viewer = ConnectionViewer()
        canvas = vpython.canvas(width=1, height=1)

        common.include_vpython_footer_file(
            Path('orbitx', 'graphics', 'simple_css.css'))

        canvas.append_to_caption("<title>OrbitX Physics Server</title>")
        canvas.append_to_caption("<h1>OrbitX Physics Server</h1>")
        canvas.append_to_caption(f"<h3>Running on {socket.getfqdn()}</h3>")

        self.clients_table = vpython.wtext(text='')

        # This is needed to launch vpython.
        vpython.sphere()
        vpython.canvas.get_selected().delete()

    def update(self):
        self.clients_table.text = \
            clients_table_formatter(self.connection_viewer.connected_clients())
        vpython.rate(self.UPDATES_PER_SECOND)


def clients_table_formatter(clients: List[str]) -> str:
    text = "blalh<table>"
    text += "<caption>Connected OrbitX clients</caption>"
    text += "<tr>"
    text += "<th scope='col'>Client</th>"
    text += "<th scope='col'>Status</th>"
    text += "</tr>"

    if len(clients) == 0:
        text += "<tr><td colspan='2'>No clients connected yet</td></tr>"

    for client in clients:
        text += "<tr>"
        text += f"<td>{client}</td>"
        text += "<td>blah client type</td>"
        text += "</tr>"

    text += "</table>"
    return text
