from typing import List, Callable

import vpython

from orbitx.graphics.flight_gui import FlightGui


# There's a bit of magic here. Normally, vpython.wtext will make a
# <div> in the HTML and automaticall update it when the .text field is
# updated in this python code. But if you want to insert a wtext in the
# middle of a field, the following first attempt won't work:
#     scene.append_to_caption('<table>')
#     vpython.wtext(text='widget text')
#     scene.append_to_caption('</table>')
# because adding the wtext will also close the <table> tag.
# But you can't make a wtext that contains HTML DOM tags either,
# because every time the text changes several times a second, any open
# dropdown menus will be closed.
# So we have to insert a <div> where vpython expects it, manually.
# We take advantage of the fact that manually modifying scene.caption
# will remove the <div> that represents a wtext. Then we add the <div>
# back, along with the id="x" that identifies the div, used by vpython.
#
# TL;DR the div_id variable is a bit magic, if you make a new wtext
# before this, increment div_id by one.
last_div_id = 1


class Text:
    def __init__(self, flight_gui: FlightGui,
                 caption: str,
                 text_gen: Callable[[], str],
                 helptext: str, *,
                 new_section: bool):
        global last_div_id
        self._wtext = vpython.wtext(text=text_gen())
        self._text_gen = text_gen
        flight_gui._scene.caption += f"""
        <tr {"class='newsection'" if new_section else ""}>
            <td>
                {caption}
            </td>
            <td class="num">
                <div id="{last_div_id}">{self._wtext.text}</div>
                <div class="helptext" style="font-size: 12px">{helptext}</div>
            </td>
        </tr>\n"""

        last_div_id += 1

    def update(self):
        self._wtext.text = self._text_gen()


class Menu:
    """Instantiate this to add a drop-down menu to the sidebar."""

    def __init__(self, flight_gui: FlightGui,
                 choices: List[str], bind: Callable, selected: str,
                 caption: str, helptext: str):
        self._menu = vpython.menu(
            choices=choices,
            bind=bind,
            selected=selected)
        flight_gui._scene.append_to_caption(f"&nbsp;<b>{caption}</b>&nbsp;")
        flight_gui._scene.append_to_caption(
            f"<span class='helptext'>{helptext}</span>\n")
