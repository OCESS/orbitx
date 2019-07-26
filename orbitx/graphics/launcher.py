import functools
from typing import List, Optional

import vpython

from orbitx import common
from orbitx import programs
from orbitx.graphics import sidebar_widgets


class Launcher:
    def __init__(self):
        # When the user clicks a button, this will be set.
        self._user_args: Optional[List[str]] = None
        self._program: Optional[programs.Program] = None

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
            .description {
                font-size: 60%;
                font-stretch: condensed;
                display: none;
            }
            .argname {
                font-weight: bold;
            }
        </style>""")

        # Set up some buttons asking what program the user wants to run.
        canvas.append_to_caption(
            "<h1>OrbitX Launcher</h1>")
        canvas.append_to_caption(
            "<h2>Select a program to launch</h2>")
        canvas.append_to_caption(
            "<input type='checkbox' id='description_checkbox'>"
            "Show descriptions"
            "</input>")

        for program in programs.LISTING:
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
                canvas.append_to_caption(
                    "<br class='description' style='display:none' />")
                canvas.append_to_caption(
                    f"<span class='argname'>{arg.dest}:</span>")
                canvas.append_to_caption(
                    "<span class='description' style='display:none'>"
                    f" {arg.help}</span>&nbsp;")
                arg_field = vpython.winput(
                    # The bind is a no-op, we'll poll the .text attribute.
                    type='string', bind=lambda _: None, text=arg.default
                )

                # Monkey-patch this attribute so that we can build CLI args
                # properly.
                arg_field.arg = arg

                text_fields.append(arg_field)
                sidebar_widgets.last_div_id += 1

        common.remove_vpython_css()

        # Make clicking the per-program launch button also submit all the args
        # that the user has entered.
        canvas.append_to_caption("""<script>
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

            description_checkbox = document.querySelector(
                '#description_checkbox');
            description_checkbox.addEventListener('change', function(event) {
                console.log(event);
                descriptions = document.getElementsByClassName("description");
                for (const element of descriptions) {
                    element.style.display = (event.target.checked ?
                        "initial" : "none"
                    );
                }
            })
        </script>""")

        # This is needed to launch vpython.
        vpython.sphere()
        vpython.canvas.get_selected().delete()

    def _set_args(self,
                  program: programs.Program,
                  arg_fields: List[vpython.winput]):
        user_args = [program.argparser.prog]
        for field in arg_fields:
            if field.arg.option_strings:
                user_args.append(field.arg.option_strings[0])
            user_args.append(field.text)
        self._user_args = user_args
        self._program = program

    def get_args(self) -> List[str]:
        while self._user_args is None:
            vpython.rate(30)

        # Disappear-ize our canvas before returning.
        vpython.canvas.get_selected().caption = ''

        return self._user_args

    def get_program(self) -> programs.Program:
        assert self._program is not None
        return self._program
