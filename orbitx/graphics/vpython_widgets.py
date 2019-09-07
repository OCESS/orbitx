from typing import Any, Callable, List, Optional

import vpython

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
last_div_id = 0


class TableText:
    """Add a row to an existing table, with first column `caption`, and
    the second column the value of `text_gen` plus an optional helptext."""
    def __init__(self,
                 caption: str,
                 text_gen: Callable[[Any], str],
                 helptext: Optional[str], *,
                 new_section: bool):
        global last_div_id
        self._wtext = vpython.wtext()
        last_div_id += 1
        self._text_gen = text_gen
        helptext = f"<div class='helptext'>{helptext}</div>" \
            if helptext else ""
        vpython.canvas.get_selected().caption += f"""
        <tr {"class='newsection'" if new_section else ""}>
            <td>
                {caption}
            </td>
            <td class="num">
                <div id="{last_div_id}">{self._wtext.text}</div>
                {helptext}
            </td>
        </tr>\n"""

    def update(self, state: Any):
        self._wtext.text = self._text_gen(state)


class Menu:
    """Instantiate this to add a drop-down menu to the sidebar."""

    def __init__(self,
                 choices: List[str], selected: str, bind: Callable,
                 caption: str, helptext: str):
        global last_div_id
        self._menu = vpython.menu(
            choices=choices, selected=selected, bind=bind)
        last_div_id += 1
        vpython.canvas.get_selected().append_to_caption(
            f"&nbsp;<b>{caption}</b>&nbsp;")
        vpython.canvas.get_selected().append_to_caption(
            f"<span class='helptext'>{helptext}</span><br/>\n")


class Checkbox:
    """Instantiate this to add a toggling checkbox to the sidebar."""

    def __init__(
            self, bind: Callable, checked: bool, text: str, helptext: str):
        global last_div_id
        last_div_id += 1
        self._checkbox = vpython.checkbox(
            text=text, bind=bind, checked=checked)
        vpython.canvas.get_selected().append_to_caption(
            f"&nbsp<span class='helptext'>{helptext}</span>\n")


class Button:
    """For something that can always be activated, as opposed to toggled."""

    def __init__(self, bind: Callable, text: str, helptext: str):
        global last_div_id
        self._button = vpython.button(text=text, bind=bind)
        last_div_id += 1
        vpython.canvas.get_selected().append_to_caption(
            f"<span class='helptext'>{helptext}</span>\n")


class Input:
    """For a text field input."""

    def __init__(self, bind: Callable, placeholder: str):
        global last_div_id
        self._winput = vpython.winput(bind=bind, type='string')
        last_div_id += 1
        vpython.canvas.get_selected().append_to_caption(f"""<script>
inp_box = document.querySelector('input[id="{last_div_id}"]');
inp_box.placeholder = "{placeholder}";
</script>""")


def stuff_widgets_into_flex_box(widget_ids: List[int], text: str = ''):
    """Stuffs the specified widgets into a div with the flex-box class."""
    query_selector = ','.join([f"[id='{wid}']" for wid in widget_ids])
    vpython.canvas.get_selected().append_to_caption(
        f"<div class='flex-box'>{text}</div>")
    vpython.canvas.get_selected().append_to_caption(f"""<script>
els = document.querySelectorAll("{query_selector}");
flex_box = document.querySelector("div.flex-box:last-of-type");
for (const element of els) {{
    flex_box.append(element);
}}
</script>""")
