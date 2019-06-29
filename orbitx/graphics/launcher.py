import argparse
import vpython
from typing import Callable

import orbitx.programs.lead


def get_user_selection() -> Callable[[argparse.Namespace], None]:
    canvas = vpython.canvas(width=1, height=1)

    # Some basic but nice styling.
    canvas.append_to_caption("""
        <style>
        body {
            margin: 1em auto;
            max-width: 40em;
            padding: 0.62em;
            font: 1.2em/1.62em sans-serif;
        }
        h1,h2,h3 {
            line-height: 1.2em;
        }
        div.ui-resizable-handle {
            /* Hide the actual vpython canvas */
            display: none !important;
            background-image: none !important;
        }
        </style>
    """)

    # Set up some buttons asking what program the user wants to run.
    canvas.append_to_caption("""<h1>
        OrbitX Launcher
    </h1>""")
    canvas.append_to_caption("""<h2>
        Select a program to launch
    </h2>""")

    canvas.append_to_caption("<hr />")
    canvas.append_to_caption("""<h3>
        Lead Flight Server
    </h3>""")
    canvas.append_to_caption("""<p>
        This program gives you piloting control of the Habitat, as it simulates
        the Habitat in spaceflight.</p>
        <p>While this lead flight server is running,
        one or more mirror programs can connect and provide a read-only copy of
        the the state of this lead flight server.
    </p>""")
    vpython.button(text='Lead Flight Server', bind=lambda x: print(x))

    # Suppress vpython styling.
    canvas.append_to_caption("""<script>
        elements = document.querySelectorAll("div,button");
        for (const element of elements) {
            element.style = null
        }
    </script>""")

    # This is needed to launch vpython.
    vpython.sphere()

    while True:
        vpython.rate(10)

    return orbitx.programs.lead.main
