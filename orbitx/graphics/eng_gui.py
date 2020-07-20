"""
Defines classes that make a tkinter GUI for Engineering
Main Application provides the root application window

The main lives inside hab_eng.py:
gui = MainApplication()
gui.mainloop()
"""

from typing import List

import tkinter as tk
import orbitx.graphics.tkinter_widgets as cw
from orbitx import strings
from orbitx.data_structures import Request

widgets = {}


class MainApplication(tk.Tk):
    """The main application window in which lives the HabPage, and potentially
    other future pages.
    Creates the file menu
    """

    def __init__(self):
        super().__init__()

        tk.Tk.wm_title(self, "OrbitX Engineering")
        self.geometry("1000x900")

        # Create menubar
        menubar = self._create_menu()
        tk.Tk.config(self, menu=menubar)

        self.label = cw.ENGLabel(self, text='Fuel', value=1000, unit='kg')
        self.label.pack()

        self._commands: List[Request] = []

    def pop_commands(self) -> List[Request]:
        """Take user input since last frame and send it off."""
        old_commands = self._commands
        self._commands = []
        return old_commands

    def contrived_keybind_function(self):
        keypress = 'a'
        if keypress == 'a':
            self._commands.append(Request(
                ident=Request.SWITCH_TOGGLE,
                switch_to_toggle=strings.COMPONENT_NAMES.index(strings.RCON1)))
        elif keypress == 'b':
            self._commands.append(Request(
                ident=Request.RADIATOR_TOGGLE,
                radiator_to_toggle=1))

    def _create_menu(self):
        menubar = tk.Menu(self)

        file = tk.Menu(menubar, tearoff=0)
        # file.add_command(label="Item1")
        file.add_command(label="Exit", command=quit)
        menubar.add_cascade(label="File", menu=file)

        return menubar

    def update_labels(self, new_value):
        self.label.value = new_value
        self.label.update()
