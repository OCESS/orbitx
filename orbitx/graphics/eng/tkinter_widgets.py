"""
Custom TKinter Widgets, reuseable across different Engineering views.

Every widget should inherit from Redrawable.
"""

from pathlib import Path
from abc import ABCMeta, abstractmethod
import tkinter as tk
from PIL import Image, ImageTk
from typing import List, Optional, Callable

from orbitx.data_structures import ComponentCoolantCnxn, EngineeringState, Request
from orbitx.programs import hab_eng
from orbitx import strings


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

    def __init__(
            self,
            parent: tk.Widget,
            row_n: int
    ):

        component_n = strings.COMPONENT_NAMES.index(parent._component_name)
        self._lp1 = CoolantButton(parent, component_n, 0).grid(row=row_n, column=0)
        self._lp2 = CoolantButton(parent, component_n, 1).grid(row=row_n, column=1)


class CoolantButton(tk.Button, Redrawable):
    """
    A component will own this button. Clicking this button will send a request
    to hook up a component to a certain coolant loop.
    """

    def __init__(
        self,
        parent: tk.Widget,
        component_n: int,
        coolant_n: int
    ):
        """
        @parent: The ComponentBlock that owns this CoolantButton.
        @component_n: The index of the component that owns this.
        @coolant_n: The number [0-2] corresponding to the coolant loop.
                    Coolant 0 is the first Hab coolant loop, and coolant 2 is
                    AYSE loop.
        """
        coolant_loop_texts = [strings.LP1, strings.LP2, strings.LP3]

        tk.Button.__init__(
            self, parent, text=coolant_loop_texts[coolant_n],
            command=self._onpress
        )
        #self.grid(fill=tk.X, expand=True)
        Redrawable.__init__(self)

        self._component_n = component_n
        self._coolant_n = coolant_n

    def _onpress(self):
        hab_eng.push_command(Request(
            ident=Request.TOGGLE_COMPONENT_COOLANT,
            component_to_loop=Request.ComponentToLoop(
                component=self._component_n, loop=self._coolant_n
            )
        ))

    def redraw(self, state: EngineeringState):
        connected_state = state.components[self._component_n].coolant_connection
        this_coolant_is_connected = False
        if self._coolant_n == 0 and (
               connected_state == ComponentCoolantCnxn.HAB_ONE or
               connected_state == ComponentCoolantCnxn.HAB_BOTH
        ):
            this_coolant_is_connected = True
        elif self._coolant_n == 1 and (
               connected_state == ComponentCoolantCnxn.HAB_TWO or
               connected_state == ComponentCoolantCnxn.HAB_BOTH
        ):
            this_coolant_is_connected = True
        elif self._coolant_n == 2 and (
               connected_state == ComponentCoolantCnxn.HAB_AYSE
        ):
            this_coolant_is_connected = True

        if this_coolant_is_connected:
            self.config(relief=tk.SUNKEN)
        else:
            self.config(relief=tk.RAISED)


class RCONFrame(tk.LabelFrame, Redrawable):
    """
    Visually represents a component, such as RCON1.
    """

    def __init__(
        self,
        parent: tk.Widget,
        component_name: str,
        optional_text_function: Optional[Callable[[EngineeringState], str]] = None,
        has_coolant_controls: bool = True, *,
        x: int, y: int
    ):
        """
        @parent: The GridPage that this will be placed in
        @optional_text: Optional. An EngineeringState->str function, this RCONFrame will reserve
                        a line of text for the output of the function and keep it updated each tick.
        @x: The x position of the top-left corner.
        @y: The y position of the top-left corner.
        """
        tk.LabelFrame.__init__(self, parent, text=component_name, labelanchor=tk.N)
        Redrawable.__init__(self)
        self.place(x=x, y=y)

        self._component_name = component_name

        self._optional_text_generator = optional_text_function
        self._optional_text_value = tk.StringVar()
        tk.Label(self, textvariable=self._optional_text_value).grid(row=0, column=0)

        self._temperature_text = tk.StringVar()
        tk.Label(self, textvariable=self._temperature_text).grid(row=0, column=1)

        if has_coolant_controls:
            CoolantSection(self, 1)
           # self._lp1 = CoolantButton(self, component_n, 0).grid(row=1, column=0)
            #self._lp2 = CoolantButton(self, component_n, 1).grid(row=1, column=1)

    def redraw(self, state: EngineeringState):
        if self._optional_text_generator is not None:
            self._optional_text_value.set(self._optional_text_generator(
                state))

        self._temperature_text.set(state.components[self._component_name].temperature)


class EngineFrame(tk.LabelFrame, Redrawable):
    def __init__(
            self,
            parent: tk.Widget,
            has_coolant_controls: bool = True, *,
            x: int, y: int
    ):
        self._component_name = "Engines"
        tk.LabelFrame.__init__(self, parent, text=self._component_name, labelanchor=tk.N)
        Redrawable.__init__(self)

        self.place(x=x, y=y)

        #Draws buttons in numerical order
        for i in range(0,4):
            tk.Button(self, text=f"GPD{i+1}").grid(row=i//2, column=i % 2)

    def redraw(self, state: EngineeringState):
        pass


class FuelFrame(tk.LabelFrame, Redrawable):
    def __init__(
            self,
            parent: tk.Widget,
            has_coolant_controls: bool = True, *,
            x: int, y: int
    ):
        self._component_name = "Habitat Fuel"
        tk.LabelFrame.__init__(self, parent, text=self._component_name, labelanchor=tk.N)
        Redrawable.__init__(self)

        self.place(x=x, y=y)

        self._fuel_count_text = tk.StringVar()
        tk.Label(self, textvariable=self._fuel_count_text).pack(side=tk.TOP)

    def redraw(self, state: EngineeringState):
        self._fuel_count_text.set(f"{state.habitat_fuel:,} kg")


class ReactorFrame(tk.LabelFrame, Redrawable):
    def __init__(
            self,
            parent: tk.Widget,
            has_coolant_controls: bool = True, *,
            x: int, y: int
    ):
        self._component_name = "Reactor"
        tk.LabelFrame.__init__(self, parent, text=self._component_name, labelanchor=tk.N)
        Redrawable.__init__(self)

        self.place(x=x, y=y)

        self._reactor_status = tk.StringVar()
        self._temperature_text = tk.StringVar()

        tk.Label(self, text="Status:").pack(side=tk.TOP)
        tk.Label(self, textvariable=self._reactor_status).pack(side=tk.TOP)
        tk.Label(self, textvariable=self._temperature_text).pack(side=tk.BOTTOM)

    def redraw(self, state: EngineeringState):
        #Temporary states
        self._reactor_status.set(f"{state.habitat_fuel:,} %")
        self._temperature_text.set(f"{state.habitat_fuel:,} %")


class RadShield(tk.LabelFrame, Redrawable):
    def __init__(
            self,
            parent: tk.Widget,
            has_coolant_controls: bool = True, *,
            x: int, y: int
    ):
        self._component_name = strings.RADS1
        tk.LabelFrame.__init__(self, parent, text=self._component_name, bg='#AADDEE', labelanchor=tk.N)
        Redrawable.__init__(self)

        self.place(x=x, y=y)

        self._rad_strength = tk.StringVar()

        component_n = strings.COMPONENT_NAMES.index(self._component_name)

        # Grid used instead of packing to organize widgets for formatting purposes
        tk.Label(self, text="Current", bg='#AADDEE').grid(row=0, column=0)
        tk.Label(self, textvariable=self._rad_strength).grid(row=0, column=1)
        tk.Button(self, text="SET", bg='#AADDEE').grid(row=1, column=0)
        tk.Entry(self, width=5).grid(row=1, column=1)

        CoolantSection(self, 2)

    def redraw(self, state: EngineeringState):
        self._rad_strength.set(f"{state.rad_shield_percentage:,} %")


class ComponentConnection(tk.Button, Redrawable):
    """
    Visually represents a switch to connect or disconnect a component from a power bus.
    """

    # Images representing a connected or disconnected switch, horizontal or vertical.
    # We can't load images
    H_CONNECTED: ImageTk.PhotoImage
    V_CONNECTED: ImageTk.PhotoImage
    H_DISCONNECTED: ImageTk.PhotoImage
    V_DISCONNECTED: ImageTk.PhotoImage

    @staticmethod
    def load_glyphs():
        """
        Call this method only once after Tk has been fully initialized.
        """
        ComponentConnection.H_CONNECTED = ImageTk.PhotoImage(Image.open(Path(
            'data', 'engineering', 'h-connected.png')))
        ComponentConnection.V_CONNECTED = ImageTk.PhotoImage(Image.open(Path(
            'data', 'engineering', 'v-connected.png')))
        ComponentConnection.H_DISCONNECTED = ImageTk.PhotoImage(Image.open(Path(
            'data', 'engineering', 'h-disconnected.png')))
        ComponentConnection.V_DISCONNECTED = ImageTk.PhotoImage(Image.open(Path(
            'data', 'engineering', 'v-disconnected.png')))

    def __init__(
        self,
        parent: tk.Widget,
        connected_component: str,
        vertical: bool = True,
        *,
        x: int, y: int
    ):
        # A button wide enough for 1 character, with no internal padding.
        tk.Button.__init__(self, parent, padx=0, pady=0)
        Redrawable.__init__(self)
        self.place(x=x, y=y)

        self._connected_component = connected_component

        if vertical:
            self._connected_glyph = ComponentConnection.V_CONNECTED
            self._disconnected_glyph = ComponentConnection.V_DISCONNECTED
        else:
            self._connected_glyph = ComponentConnection.H_CONNECTED
            self._disconnected_glyph = ComponentConnection.H_DISCONNECTED

    def redraw(self, state: EngineeringState):
        connected = state.components[self._connected_component].connected
        if connected:
            self.configure(image=self._connected_glyph)
        else:
            self.configure(image=self._disconnected_glyph)
