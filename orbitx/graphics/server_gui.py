"""A simple textual GUI for the Physics Server."""

import logging
import socket
import time
from pathlib import Path
from types import SimpleNamespace
from typing import List

import vpython

from orbitx import common
from orbitx.data_structures import savefile
from orbitx.data_structures.space import PhysicsState
from orbitx.graphics import vpython_widgets

log = logging.getLogger('orbitx')


class ServerGui:
    UPDATES_PER_SECOND = 10

    def __init__(self):
        self._commands: List[common.Request] = []
        self._last_state_for_saving: PhysicsState
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
            bind=self._save_hook, placeholder='Save savefile')
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
        self._previous_number_of_clients: int = 0

        # This is needed to launch vpython.
        vpython.sphere()
        canvas.delete()
        common.remove_vpython_css()

    def pop_commands(self) -> List[common.Request]:
        """Take gathered user input and send it off."""
        old_commands = self._commands
        self._commands = []
        return old_commands

    def update(self, state: PhysicsState, clients: List[SimpleNamespace]):
        if len(clients) != self._previous_number_of_clients:
            # We only want to change the DOM when there is a change in clients,
            # which we notice when the cached list of unique client identifiers
            # changes.
            self._previous_number_of_clients = len(clients)
            self._build_clients_table(clients)

        current_time = time.monotonic()
        for wtext, client in zip(self._last_contact_wtexts, clients):
            relative_last_message_time = current_time - client.last_contact

            wtext.text = f'{relative_last_message_time:.1f} seconds ago'

        self._last_state_for_saving = state
        vpython.rate(self.UPDATES_PER_SECOND)

    def _build_clients_table(self, clients: List[SimpleNamespace]):
        text = "<table>"
        text += "<caption>Connected OrbitX clients</caption>"
        text += "<tr>"
        text += "<th scope='col'>Client</th>"
        text += "<th scope='col'>Location</th>"
        text += "<th scope='col'>Last Contact</th>"
        text += "</tr>"
        self._last_contact_wtexts = []

        if len(clients) == 0:
            text += \
                "<tr><td colspan='3'>No currently connected clients</td></tr>"

        for client in clients:
            self._last_contact_wtexts.append(vpython.wtext(text=''))
            vpython_widgets.last_div_id += 1
            text += "<tr>"
            text += f"<td>{client.client_type}</td>"
            text += f"<td>{client.client_addr}</td>"
            text += f"<td><div id={vpython_widgets.last_div_id}>Connecting"
            text += "</div></td></tr>"

        text += "</table>"
        self._clients_table.text = text

    def _save_hook(self, textbox: vpython.winput):
        full_path = savefile.full_path(textbox.text)
        try:
            full_path = savefile.write_savefile(self._last_state_for_saving, full_path)
            textbox.text = f'Saved to {full_path}!'
        except OSError:
            log.exception('Caught exception during file saving')
            textbox.text = f'Error writing file to {full_path}'

    def _load_hook(self, textbox: vpython.winput):
        full_path = savefile.full_path(textbox.text)
        if full_path.is_file():
            self._commands.append(common.Request(
                ident=common.Request.LOAD_SAVEFILE, loadfile=textbox.text))
            textbox.text = f'Loaded {full_path}!'
        else:
            log.warning(f'Ignored non-existent loadfile: {full_path}')
            textbox.text = f'{full_path} not found!'
