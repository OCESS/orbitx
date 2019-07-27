"""A simple textual GUI for the Physics Server."""

import time
from pathlib import Path
from typing import Dict

import vpython

import orbitx.common as common

# How many seconds until a client is considered stale.
CLIENT_STALE_SECONDS = 4.


class ServerGui:
    UPDATES_PER_SECOND = 10

    def __init__(self):
        canvas = vpython.canvas(width=1, height=1)

        canvas.append_to_caption("<title>OrbitX Physics Server</title>")
        canvas.append_to_caption("<h1>OrbitX Physics Server</h1>")

        self.clients_table = vpython.wtext(text='')

        common.include_vpython_footer_file(
            Path('orbitx', 'graphics', 'simple_css.css'))

        # This is needed to launch vpython.
        vpython.sphere()
        vpython.canvas.get_selected().delete()

    def update(self, client_map: Dict[str, float]):
        self.clients_table.text = clients_table_formatter(client_map)
        vpython.rate(self.UPDATES_PER_SECOND)


def clients_table_formatter(clients_map: Dict[str, float]) -> str:
    text = "<table>"
    text += "<caption>Connected OrbitX clients</caption>"
    text += "<tr>"
    text += "<th scope='col'>Client</th>"
    text += "<th scope='col'>Status</th>"
    text += "</tr>"

    if len(clients_map) == 0:
        text += "<tr><td colspan='2'>No clients connected yet</td></tr>"

    monotime = time.monotonic()
    for client, last_time in clients_map.items():
        text += "<tr>"
        text += f"<td>{client}</td>"
        if monotime - last_time > CLIENT_STALE_SECONDS:
            text += "<td>Stale</td>"
        else:
            text += "<td>Active</td>"
        text += "</tr>"

    text += "</table>"
    return text
