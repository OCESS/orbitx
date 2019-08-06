"""A simple textual GUI for the Physics Server."""

import calendar
import logging
import socket
import time
from pathlib import Path
from typing import Dict, List, NamedTuple, Optional

from grpc._cython import cygrpc
from google.protobuf import json_format
from google.protobuf.timestamp_pb2 import Timestamp
from grpc_channelz.v1 import channelz_pb2
import vpython

from orbitx import common

log = logging.getLogger()

TZ_OFFSET_SECONDS = \
    calendar.timegm(time.gmtime()) - calendar.timegm(time.localtime())


class ClientConnection(NamedTuple):
    """Represents data about a client connection."""
    location: str
    socket: channelz_pb2.Socket


class ConnectionViewer:
    """Queries C-Core channelz statistics to see what clients have open channels
    with this GRPC process."""
    def __init__(self):
        self._target_server_id: Optional[int] = None

    def connected_clients(self) -> List[ClientConnection]:
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
        connections = []
        for ssock in ssockets.socket_ref:
            connections.append(ClientConnection(
                ssock.name,
                json_format.Parse(
                    cygrpc.channelz_get_socket(ssock.socket_id),
                    channelz_pb2.GetSocketResponse()
                )
            ))
        return connections


class ServerGui:
    UPDATES_PER_SECOND = 10

    # See comments in sidebar_widgets.py for why this is needed.
    _last_vpython_div_id = 0

    def __init__(self):
        self.connection_viewer = ConnectionViewer()
        canvas = vpython.canvas(width=1, height=1)

        common.include_vpython_footer_file(
            Path('orbitx', 'graphics', 'simple_css.css'))

        # Hide vpython wtexts, except for the table.
        canvas.append_to_caption("""<style>
            span {
                display: none;
            }
            span[id="1"] {
                display: initial;
            }
        </style>""")

        canvas.append_to_caption("<title>OrbitX Physics Server</title>")
        canvas.append_to_caption("<h1>OrbitX Physics Server</h1>")
        canvas.append_to_caption(f"<h3>Running on {socket.getfqdn()}</h3>")

        self._clients_table = vpython.wtext(text='')
        self._last_vpython_div_id += 1
        self._last_contact_wtexts: List[vpython.wtext] = []
        self._last_client_locs = None

        # This is needed to launch vpython.
        vpython.sphere()
        vpython.canvas.get_selected().delete()

    def update(self, client_types: Dict[str, str]):
        connected_clients = self.connection_viewer.connected_clients()
        current_client_locs = [
            client.location for client in connected_clients
        ]

        if current_client_locs != self._last_client_locs and \
                all(client in client_types for client in current_client_locs):
            # We only want to change the DOM when there is a change in clients,
            # which we notice when the cached list of unique client identifiers
            # changes.
            self._last_client_locs = current_client_locs
            self.build_clients_table(connected_clients, client_types)
            # By clearing this dict, we keep stale items out of it and allow
            # them to be populated with fresher values.
            client_types.clear()

        current_time = Timestamp()
        current_time.GetCurrentTime()
        for wtext, client in zip(self._last_contact_wtexts, connected_clients):
            last_contact = \
                client.socket.socket.data.last_message_received_timestamp
            relative_last_message_time = (
                (current_time.seconds + current_time.nanos / 1e9) -
                (last_contact.seconds + last_contact.nanos / 1e9)
            )

            # I think just on Windows, this time difference might be off by
            # the time zone, make an adjustment for that.
            relative_last_message_time %= TZ_OFFSET_SECONDS

            wtext.text = f'{relative_last_message_time:.1f} seconds ago'

        vpython.rate(self.UPDATES_PER_SECOND)

    def build_clients_table(self,
                            connections: List[ClientConnection],
                            client_types: Dict[str, str]):
        text = "<table>"
        text += "<caption>Connected OrbitX clients</caption>"
        text += "<tr>"
        text += "<th scope='col'>Client</th>"
        text += "<th scope='col'>Location</th>"
        text += "<th scope='col'>Last Contact</th>"
        text += "</tr>"
        self._last_contact_wtexts = []

        if len(connections) == 0:
            text += \
                "<tr><td colspan='3'>No currently connected clients</td></tr>"

        for client in connections:
            try:
                client_type = client_types[client.location]
            except KeyError:
                client_type = '&nbsp;'

            self._last_contact_wtexts.append(vpython.wtext(text=''))
            self._last_vpython_div_id += 1
            text += "<tr>"
            text += f"<td>{client_type}</td>"
            text += f"<td>{client.location}</td>"
            text += f"<td><div id={self._last_vpython_div_id}></div></td>"
            text += "</tr>"

        text += "</table>"
        self._clients_table.text = text
