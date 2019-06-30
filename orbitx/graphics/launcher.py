import functools
from typing import Optional

import vpython

from orbitx.common import Program
from orbitx.programs.lead import Lead
from orbitx.programs.mirror import Mirror
from orbitx.programs.compat import Compat


class Launcher:
    def __init__(self):
        # When the user clicks a button, this will be set.
        self.selected_program: Optional[Program] = None

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
            vpython.button(
                text=program.name,
                bind=functools.partial(self._set_selection, program))

        # Suppress vpython styling.
        canvas.append_to_caption("""<script>
            elements = document.querySelectorAll("div,button");
            for (const element of elements) {
                element.style = null
            }
        </script>""")

        # This is needed to launch vpython.
        vpython.sphere()
        vpython.canvas.get_selected().delete()

    def _set_selection(self, program: Program):
        self.selected_program = program

    def get_user_selection(self) -> Program:
        while self.selected_program is None:
            vpython.rate(30)

        # Disappear-ize our canvas before returning.
        vpython.canvas.get_selected().caption = ''

        return self.selected_program
