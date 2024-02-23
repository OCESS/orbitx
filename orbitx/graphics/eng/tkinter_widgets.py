"""
Custom TKinter Widgets, reuseable across different Engineering views.

Every widget should inherit from Redrawable.
"""

from pathlib import Path
from abc import ABCMeta, abstractmethod
import logging
import tkinter as tk
from PIL import Image, ImageTk
import re
from typing import Callable, NamedTuple, Optional, List, Union

from orbitx.common import Request
from orbitx.data_structures.engineering import EngineeringState
from orbitx.programs import hab_eng
from orbitx import strings

log = logging.getLogger('orbitx')

INNER_TEXT_MARGIN = 2


class Coords(NamedTuple):
    x: int
    y: int
    width: int
    height: int


class Redrawable(metaclass=ABCMeta):
    """Inherit all custom widgets from this. Automatically registers instantiated
    objects that inherit from this, which makes life easier.

    Usage:

        class MyWidget(Redrawable):
            def __init__(self, blah, blooh, blah):
                [your widget code here]
                self._changeable_field_or_whatever = tk.StringVar()

            def redraw(self, state: EngineeringState):
                # If you forget to define this method, Python will give you an error.
                # Just an example of using a tkinter StringVar
                self._changeable_field_or_whatever.set(state.habitat_fuel)

        MyWidget(arguments)
        # That's it! main_window.py will automatically call redraw() on your widget!
    """

    # Contains all instantiated Redrawables. Loop over this to redraw them all.
    all_instantiated_widgets: List['Redrawable'] = []

    @abstractmethod
    def redraw(self, state: EngineeringState) -> None:
        """Ensures that inherited classes must define a redraw function."""
        pass

    def __init__(self):
        """Automatically registers an instantiated subclass."""
        Redrawable.all_instantiated_widgets.append(self)


class DetailsFrame(tk.Frame, Redrawable):
    """
    Displays information about the currently-selected component in
    the bottom left of the window.

    Most fields are common to all components (name, description, current,
    etc.), but some components might have a unique field or two (rad
    shield setting, reactor status).
    """

    def __init__(self, parent: tk.Widget):
        tk.Frame.__init__(self, parent)
        Redrawable.__init__(self)


class WarningsFrame(tk.Frame, Redrawable):
    """
    Displays a list of warnings in a frame at the bottom of the window,
    next to DetailsFrame.
    """

    def __init__(self, parent: tk.Widget):
        tk.Frame.__init__(self, parent)
        Redrawable.__init__(self)


class CoolantSection():
    """
    Contains two coolant buttons horizontally side by side. Places these coolant
    buttons on a given row inside a widget.
    """

    def __init__(self, parent: tk.Widget, row_n: int):

        component_n = strings.COMPONENT_NAMES.index(parent._component_name)
        self._lp1 = CoolantButton(parent, component_n, 0)
        self._lp1.grid(row=row_n, column=0)
        self._lp2 = CoolantButton(parent, component_n, 1)
        self._lp2.grid(row=row_n, column=1)


class CoolantButton(tk.Button, Redrawable):
    """
    A component will own this button. Clicking this button will send a request
    to hook up a component to a certain coolant loop.
    """

    def __init__(self, parent: tk.Widget, component_n: int, coolant_n: int):
        """
        @parent: The ComponentBlock that owns this CoolantButton.
        @component_n: The index of the component that owns this.
        @coolant_n: The number [0-2] corresponding to the coolant loop.
                    Coolant 0 is the first Hab coolant loop, and coolant 2 is
                    AYSE loop.
        """
        coolant_loop_texts = [strings.LP1, strings.LP2, strings.LP3]

        tk.Button.__init__(self, parent, text=coolant_loop_texts[coolant_n], command=self._onpress)
        Redrawable.__init__(self)

        self._component_n = component_n
        self._coolant_n = coolant_n

    def _onpress(self):
        hab_eng.push_command(
            Request(ident=Request.TOGGLE_COMPONENT_COOLANT,
                    component_to_loop=Request.ComponentToLoop(component=self._component_n, loop=self._coolant_n)))

    def redraw(self, state: EngineeringState):

        component = state.components[self._component_n]
        if state.coolant_loops[self._coolant_n] in component.connected_coolant_loops():
            self.config(relief=tk.SUNKEN)
        else:
            self.config(relief=tk.RAISED)


class SimpleText(tk.LabelFrame, Redrawable):
    """
    Redrawable of a simple box, with the inner text controlled by a StringVar

    Args:
        parent (tk.Widget): Required by tkinter, the parent widget that this is created in.
        inner_text (tk.StringVar or str): The initial text in the widget (a str will be converted to a StringVar)
        coords (Coords): the x, y, width, and height of the widget

    Attributes:
        stringvar (tk.StringVar): Update this to change the text of the widget
    """

    _stringvar: tk.StringVar
    _text_generator: Callable[[EngineeringState], str]

    def __init__(self, parent: tk.Widget, coords: Coords, text_function: Callable[[EngineeringState], str]):
        self._stringvar = tk.StringVar()
        tk.Label.__init__(self, parent, textvariable=self._stringvar, wraplength=coords.width - INNER_TEXT_MARGIN, relief='ridge')
        Redrawable.__init__(self)
        self.place(x=coords.x, y=coords.y, width=coords.width, height=coords.height)
        self._text_generator = text_function

    def redraw(self, state: EngineeringState):
        self._stringvar.set(self._text_generator(state))


class RCONFrame(SimpleText):
    """
    Visually represents a component, such as RCON1.
    """

    def __init__(self,
                 parent: tk.Widget,
                 coords: Coords,
                 text_function: Callable[[EngineeringState], str],
                 has_coolant_controls: bool = True,):
        """
        @parent: The GridPage that this will be placed in
        @optional_text: Optional. An EngineeringState->str function, this RCONFrame will reserve
                        a line of text for the output of the function and keep it updated each tick.
        @x: The x position of the top-left corner.
        @y: The y position of the top-left corner.
        """
        SimpleText.__init__(self, parent=parent, coords=coords, text_function=text_function)

        self.place(x=coords.x, y=coords.y)

        self._optional_text_value = tk.StringVar()
        tk.Label(self, textvariable=self._optional_text_value).grid(row=0, column=0)

        self._temperature_text = tk.StringVar()
        tk.Label(self, textvariable=self._temperature_text).grid(row=0, column=1)


class EngineFrame(SimpleText):

    def __init__(self, parent: tk.Widget, coords: Coords, text_function: Callable[[EngineeringState], str]):
        """
        @parent: The GridPage that this will be placed in.
        @x: The x position of the top-left corner.
        @y: The y position of the top-left corner.
        """
        super(EngineFrame, self).__init__(parent, coords, text_function)

        self.place(x=coords.x, y=coords.y)

    def redraw(self, state: EngineeringState):
        pass


class RadShieldFrame(tk.LabelFrame, Redrawable):

    def __init__(self, parent: tk.Widget, component_name: str, *, coords: Coords):
        """
        @parent: The GridPage that this will be placed in.
        @x: The x position of the top-left corner.
        @y: The y position of the top-left corner.
        """
        self._component_name = strings.RADS1
        tk.LabelFrame.__init__(self, parent, text=self._component_name, bg='#AADDEE', labelanchor=tk.N)
        Redrawable.__init__(self)

        self.place(x=coords.x, y=coords.y)

        self._rad_strength = tk.StringVar()

        # Grid used instead of packing to organize widgets for formatting purposes
        tk.Label(self, text="Current", bg='#AADDEE').grid(row=0, column=0)
        tk.Label(self, textvariable=self._rad_strength).grid(row=0, column=1)
        tk.Button(self, text="SET", bg='#AADDEE').grid(row=1, column=0)
        tk.Entry(self, width=5).grid(row=1, column=1)

        CoolantSection(self, 2)

    def redraw(self, state: EngineeringState):
        self._rad_strength.set(f"{state.rad_shield_percentage:,} %")


class PowerBusFrame(tk.LabelFrame, Redrawable):

    def __init__(self, parent: tk.Widget, component_name: str, *, coords: Coords):

        tk.LabelFrame.__init__(self, parent, text=component_name, labelanchor=tk.N)
        self._component_name = component_name
        Redrawable.__init__(self)

        self.place(x=coords.x, y=coords.y)

        self._power = tk.StringVar()
        self._current = tk.StringVar()
        self._voltage = tk.StringVar()

        tk.Label(self, text="Power: ").grid(row=0, column=0)
        tk.Label(self, textvariable=self._power).grid(row=0, column=1)
        tk.Label(self, text="Current: ").grid(row=0, column=2)
        tk.Label(self, textvariable=self._current).grid(row=0, column=3)
        tk.Label(self, text="Voltage: ").grid(row=0, column=4)
        tk.Label(self, textvariable=self._voltage).grid(row=0, column=5)

    def redraw(self, state: EngineeringState):
        bus_electricals = state.BusElectricals()[self._component_name]
        self._power.set(str(bus_electricals.current * bus_electricals.voltage))
        self._current.set(str(bus_electricals.current))
        self._voltage.set(str(bus_electricals.voltage))
