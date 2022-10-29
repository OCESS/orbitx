# -*- coding: utf-8 -*-
"""A simple textual GUI for the compat client."""

import functools
from datetime import datetime
from pathlib import Path
from typing import List, Set

import grpc
import vpython

from orbitx import common
from orbitx import orbitx_pb2
from orbitx.graphics import vpython_widgets
from orbitx.orbitv_file_interface import OrbitVIntermediary
from orbitx.strings import OCESS


class CompatGui:
    UPDATES_PER_SECOND = 1
    ORBITSSE_STALE_SECONDS = 10

    def __init__(self, server_name: str, intermediary: OrbitVIntermediary):
        self._orbitsse_path = intermediary.orbitsse
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
            "<div>"
            f"Writing to <span class='mono'>{intermediary.osbackup}</span>"
            "</div>")

        self._osbackup_write_time_field = vpython.wtext(text='')
        vpython_widgets.last_div_id += 1
        canvas.append_to_caption(
            "<div>"
            "<span>Last update written at</span> "
            f"<span class='mono' id='{vpython_widgets.last_div_id}'></span>"
            "</div>")

        self._orbitv_entities = set(intermediary.orbitv_names)
        self._last_missing_entities_set: Set[str] = set()
        self._missing_entities_warning = vpython.wtext(text='')
        vpython_widgets.last_div_id += 1
        canvas.append_to_caption(
            f"<div id='{vpython_widgets.last_div_id}'></div>")

        canvas.append_to_caption("<h3>OrbitX ← OrbitV</h3>")
        canvas.append_to_caption(
            "<div>"
            f"Reading from <span class='mono'>{intermediary.orbitsse}</span>"
            "</div>")

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

        def row_text_setter(eng_update: common.Request.OrbitVEngineeringUpdate,
                            field_name: str) -> str:
            return getattr(eng_update, field_name)

        fields_list = orbitx_pb2.Command.OrbitVEngineeringUpdate.DESCRIPTOR.fields
        self._eng_fields: List[vpython_widgets.TableText] = []
        for descriptor in fields_list:
            self._eng_fields.append(vpython_widgets.TableText(
                descriptor.name.replace('_', ' ').title(),
                functools.partial(row_text_setter, field_name=descriptor.name),
                None,
                new_section=False))

        canvas.append_to_caption("</table>")

        # This is needed to launch vpython.
        vpython.sphere()
        canvas.delete()
        common.remove_vpython_css()

    def update(self, eng_update: common.Request, orbitx_names: List[str],
               last_orbitsse_read_datetime: datetime):
        if eng_update.ident == common.Request.ENGINEERING_UPDATE:
            for field in self._eng_fields:
                field.update(eng_update.engineering_update)

        set_difference = self._orbitv_entities - set(orbitx_names)
        # Only change the missing entity warning message if needed, since
        # changing the DOM multiple times a second isn't great.
        if set_difference != self._last_missing_entities_set:
            # The set of entities in OrbitV but not in OrbitX changed.
            self._last_missing_entities_set = set_difference
            if len(set_difference) == 0:
                self._missing_entities_warning.text = ""
            else:
                self._missing_entities_warning.text = (
                    "<b>Warning:</b> OrbitV is expecting entities that do not "
                    "exist in OrbitX. These following entities will be wrong: "
                    "<span class='mono'>"
                )
                self._missing_entities_warning.text += \
                    ", ".join(set_difference)
                self._missing_entities_warning.text += "</span>."

                if OCESS in set_difference:
                    self._missing_entities_warning.text += (
                        " (OCESS has not been implemented in OrbitX yet, "
                        "sorry!)"
                    )

        self._osbackup_write_time_field.text = datetime.now().strftime('%X')

        field_text = last_orbitsse_read_datetime.strftime('%x %X')
        if (datetime.now() - last_orbitsse_read_datetime).total_seconds() > \
                self.ORBITSSE_STALE_SECONDS:
            field_text += " <b>(stale?)</b>"
        self._orbitsse_read_time_field.text = field_text

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
        canvas.append_to_caption("<title>OrbitX Error</title>")
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
