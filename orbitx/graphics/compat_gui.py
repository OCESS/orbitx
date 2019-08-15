# -*- coding: utf-8 -*-
"""A simple textual GUI for the compat client."""


import functools
from datetime import datetime
from pathlib import Path
from typing import List

import grpc
import vpython

from orbitx import common
from orbitx import network
from orbitx import orbitx_pb2
from orbitx.graphics import vpython_widgets


class CompatGui:
    UPDATES_PER_SECOND = 5
    ORBITSSE_STALE_SECONDS = 10

    def __init__(self, server_name: str, osbackup: Path, orbitsse: Path):
        self._orbitsse_path = orbitsse
        canvas = vpython.canvas(width=1, height=1)

        common.include_vpython_footer_file(
            Path('orbitx', 'graphics', 'simple_css.css'))

        canvas.append_to_caption("<title>OrbitX Compat Client</title>")
        canvas.append_to_caption(
            "<h1>OrbitX ↔ OrbitV Piloting Compatibility")
        canvas.append_to_caption(
            f"<h3>Connected to Physics Server at {server_name}</h3>")

        self._error_field = vpython.wtext(text='')
        vpython_widgets.last_div_id += 1
        canvas.append_to_caption(
            f"<div id={vpython_widgets.last_div_id}></div>")

        canvas.append_to_caption("<h3>OrbitX → OrbitV</h3>")
        canvas.append_to_caption(
            f"<div>Writing to <span class='mono'>{osbackup}</span></div>")

        self._osbackup_write_time_field = vpython.wtext(text='')
        vpython_widgets.last_div_id += 1
        canvas.append_to_caption(
            "<div>"
            "<span>Last update written at</span> "
            f"<span class='mono' id='{vpython_widgets.last_div_id}'></span>"
            "</div>")

        canvas.append_to_caption("<h3>OrbitX ← OrbitV</h3>")
        canvas.append_to_caption(
            f"<div>Reading from <span class='mono'>{orbitsse}</span></div>")

        self._orbitsse_read_time_field = vpython.wtext(text='')
        vpython_widgets.last_div_id += 1
        canvas.append_to_caption(
            "<div>"
            "<span>Last update detected and read at</span> "
            f"<span class='mono' id='{vpython_widgets.last_div_id}'></span>"
            "</div>")

        canvas.append_to_caption("<table>\n")
        canvas.append_to_caption(
            "<caption>Contents of last OrbitV Engineering update</caption>")
        canvas.append_to_caption("<tr>")
        canvas.append_to_caption("<th scope='col'>Field name</th>")
        canvas.append_to_caption("<th scope='col'>Field value</th>")
        canvas.append_to_caption("</tr>")

        def row_text_setter(eng_update: network.Request.EngineeringUpdate,
                            field_name: str) -> str:
            return getattr(eng_update, field_name)

        fields_list = orbitx_pb2.Command.EngineeringUpdate.DESCRIPTOR.fields
        self._eng_fields: List[vpython_widgets.TableText] = []
        for descriptor in fields_list:
            print(repr(descriptor.name))
            self._eng_fields.append(vpython_widgets.TableText(
                descriptor.name.replace('_', ' '),
                functools.partial(row_text_setter, field_name=descriptor.name),
                None,
                new_section=False))

        canvas.append_to_caption("</table>")

        # This is needed to launch vpython.
        vpython.sphere()
        canvas.delete()
        common.remove_vpython_css()

    def update(self, eng_update: network.Request,
               last_orbitsse_read_datetime: datetime):
        if eng_update.ident == network.Request.ENGINEERING_UPDATE:
            for field in self._eng_fields:
                field.update(eng_update.engineering_update)
        self._osbackup_write_time_field.text = datetime.now().strftime('%X')

        field_text = last_orbitsse_read_datetime.strftime('%x %X')
        if (datetime.now() - last_orbitsse_read_datetime).total_seconds() > \
                self.ORBITSSE_STALE_SECONDS:
            field_text += " (stale?)"
        self._orbitsse_read_time_field.text = field_text
        # Write when orbitssew was last modified
        vpython.rate(self.UPDATES_PER_SECOND)

    def notify_shutdown(self, error: grpc.RpcError):
        self._error_field.text = (f"""<div class='error'>
            Received <span class='mono'>{error.code()}</span>
            from Physics Server. Shutting down.</div>""")


class StartupFailedGui:
    """Only shows a connection failed message."""

    def __init__(self, server_name: str, error: grpc.RpcError):
        canvas = vpython.canvas(width=1, height=1)

        common.include_vpython_footer_file(
            Path('orbitx', 'graphics', 'simple_css.css'))

        # TODO: failed connec
        canvas.append_to_caption("<title>OrbitX Compat Client</title>")
        canvas.append_to_caption(
            "<h1>OrbitX ↔ OrbitV Piloting Compatibility")
        canvas.append_to_caption(
            f"<h3>Tried connecting to Physics Server at {server_name}</h3>")
        canvas.append_to_caption(f"""<div class='error'>
            But the network connection failed to start
            (<span class='mono'>{error.code()}</span>).
            {"The Physics Server might be not running, or it might be running "
             "on a different host."
             if error.code() == grpc.StatusCode.UNAVAILABLE else ""}
        </div>""")

        # This is needed to launch vpython.
        vpython.sphere()
        canvas.delete()
        common.remove_vpython_css()
