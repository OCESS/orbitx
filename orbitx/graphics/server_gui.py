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
from orbitx import network
from orbitx.data_structures import PhysicsState
from orbitx.graphics import vpython_widgets

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

    def __init__(self):
        self._commands: List[network.Request] = []
        self._last_state: PhysicsState
        self.connection_viewer = ConnectionViewer()
        canvas = vpython.canvas(width=1, height=1)

        common.include_vpython_footer_file(
            Path('orbitx', 'graphics', 'simple_css.css'))

        # Hide vpython wtexts, except for the table.
        canvas.append_to_caption("""<style>
            span {
                /* Hide any wtexts we generate. */
                display: none;
            }
            span.nohide {
                /* Make sure wtexts we make are not hidden. */
                display: initial;
            }
            div.flex-box {
                display: flex;
                justify-content: space-between;
            }
            input {
                flex: 1;
                margin: 5px;
            }
        </style>""")

        canvas.append_to_caption("<title>OrbitX Physics Server</title>")
        canvas.append_to_caption("<h1>OrbitX Physics Server</h1>")
        canvas.append_to_caption(f"<h3>Running on {socket.getfqdn()}</h3>")

        canvas.append_to_caption("<div class='flex-box'></div>")

        vpython_widgets.Input(
            bind=self._load_hook, placeholder='Load savefile')
        vpython_widgets.Input(
            bind=self._load_hook, placeholder='Save savefile')
        vpython_widgets.stuff_widgets_into_flex_box([
            vpython_widgets.last_div_id - 1, vpython_widgets.last_div_id
        ])

        canvas.append_to_caption("<hr />")

        self._clients_table = vpython.wtext(text='')
        vpython_widgets.last_div_id += 1
        # We hide all other vpython-made wtexts, except for this one.
        canvas.append_to_caption(f"""<script>
document.querySelector(
    'span[id="{vpython_widgets.last_div_id}"]').className = 'nohide';
</script>""")
        self._last_contact_wtexts: List[vpython.wtext] = []
        self._last_client_locs: Optional[List[str]] = None

        # This is needed to launch vpython.
        vpython.sphere()
        canvas.delete()
        common.remove_vpython_css()

    def pop_commands(self) -> List[network.Request]:
        """Take gathered user input and send it off."""
        old_commands = self._commands
        self._commands = []
        return old_commands

    def update(self, state: PhysicsState, client_types: Dict[str, str]):
        self._last_state = state
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
            self._build_clients_table(connected_clients, client_types)
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

    def _build_clients_table(self,
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
            vpython_widgets.last_div_id += 1
            text += "<tr>"
            text += f"<td>{client_type}</td>"
            text += f"<td>{client.location}</td>"
            text += f"<td><div id={vpython_widgets.last_div_id}></div></td>"
            text += "</tr>"

        text += "</table>"
        self._clients_table.text = text

    def _save_hook(self, textbox: vpython.winput):
        full_path = common.savefile(textbox.text)
        try:
            full_path = common.write_savefile(self._last_state, full_path)
            textbox.text = f'Saved to {full_path}!'
        except OSError:
            log.exception('Caught exception during file saving')
            textbox.text = f'Error writing file to {full_path}'

    def _load_hook(self, textbox: vpython.winput):
        full_path = common.savefile(textbox.text)
        if full_path.is_file():
            self._commands.append(network.Request(
                ident=network.Request.LOAD_SAVEFILE, loadfile=textbox.text))
            textbox.text = f'Loaded {full_path}!'
        else:
            log.warning(f'Ignored non-existent loadfile: {full_path}')
            textbox.text = f'{full_path} not found!'
