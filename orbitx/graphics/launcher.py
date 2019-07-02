import functools
from typing import List, Optional

import vpython

from orbitx.common import Program
from orbitx.programs.lead import Lead
from orbitx.programs.mirror import Mirror
from orbitx.programs.compat import Compat


class Launcher:
    def __init__(self):
        # When the user clicks a button, this will be set.
        self._user_args: Optional[List[str]] = None

        canvas = vpython.canvas(width=1, height=1)

        # Some basic but nice styling.
        canvas.append_to_caption("""<style>
            body {
                margin: 1em auto;
                max-width: 40em;
                padding: 0.62em;
                font: 1.2em/1.62em sans-serif;
            }
            h1,h2,h3 {
                line-height: 1.2em;
            }
        </style>""")

        # Set up some buttons asking what program the user wants to run.
        canvas.append_to_caption("""<h1>
            OrbitX Launcher
        </h1>""")
        canvas.append_to_caption("""<h2>
            Select a program to launch
        </h2>""")

        for program in [Lead, Mirror, Compat]:
            canvas.append_to_caption("<hr />")
            canvas.append_to_caption(f"<h3>{program.name}</h3>")
            canvas.append_to_caption(f"<p>{program.description}</p>")
            text_fields: List[vpython.winput] = []
            vpython.button(
                text=program.name,
                bind=functools.partial(self._set_args, program, text_fields))
            for arg in program.argparser._actions:
                if '--help' in arg.option_strings:
                    # This is the default help action, ignore it.
                    continue
                canvas.append_to_caption(arg.dest + ":&nbsp;")
                arg_field = vpython.winput(
                    # The bind is a no-op, we'll poll the .text attribute.
                    type='string', bind=lambda _: None, text=arg.default
                )

                # Monkey-patch this attribute so that we can build CLI args
                # properly.
                arg_field.arg = arg

                text_fields.append(arg_field)

        # Suppress vpython styling.
        canvas.append_to_caption("""<script>
            styled_elements = document.querySelectorAll("div,button");
            for (const element of styled_elements) {
                element.style = null
            }

            buttons = document.querySelectorAll("button");
            for (const element of buttons) {
                element.addEventListener('mousedown', function(ev) {
                    // Send an 'enter' keypress so that python code gets the
                    // current value of each text input.
                    inputs = document.querySelectorAll('input');
                    for (const input of inputs) {
                        var ev = document.createEvent('Event');
                        ev.initEvent('keypress');
                        ev.keyCode = 13;
                        input.dispatchEvent(ev);
                    }
                });
            }
        </script>""")

        # This is needed to launch vpython.
        vpython.sphere()
        vpython.canvas.get_selected().delete()

    def _set_args(self, program: Program, arg_fields: List[vpython.winput]):
        self._user_args = [program.argparser.prog]
        for field in arg_fields:
            if field.arg.option_strings:
                self._user_args.append(field.arg.option_strings[0])
            self._user_args.append(field.text)

    def get_args(self) -> List[str]:
        while self._user_args is None:
            vpython.rate(30)

        # Disappear-ize our canvas before returning.
        vpython.canvas.get_selected().caption = ''

        return self._user_args
