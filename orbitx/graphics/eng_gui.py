"""
Defines FlightGui, a class that provides a main loop for flight.

Call FlightGui.draw() in the main loop to update positions in the GUI.
Call FlightGui.pop_commands() to collect user input.
"""

import logging
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional

import tkinter as tk
# import custom_widgets as cw
# import eng_engine as eng

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

        # Initialise main page
        self.page = HabPage(self)
        self.page.pack(side=tk.TOP, expand=True, fill=tk.BOTH)

    def _create_menu(self):
        menubar = tk.Menu(self)

        file = tk.Menu(menubar, tearoff=0)
        # file.add_command(label="Item1")
        file.add_command(label="Exit", command=quit)
        menubar.add_cascade(label="File", menu=file)

        return menubar
