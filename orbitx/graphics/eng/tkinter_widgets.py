"""
Custom TKinter Widgets, reuseable across different Engineering views.

Every widget should inherit from Redrawable.
"""

import re
from pathlib import Path
from abc import ABCMeta, abstractmethod
import logging
import tkinter as tk
import tkinter.ttk as ttk
from PIL import Image, ImageTk
import xml.etree.ElementTree as ET
from typing import Callable, Dict, NamedTuple, Optional, List

from orbitx.common import Request
from orbitx.data_structures.engineering import EngineeringState
from orbitx.programs import hab_eng
from orbitx import strings

log = logging.getLogger('orbitx')

INNER_TEXT_MARGIN = 2
AUX_BUTTON_MARGIN = 36

BORDER_WIDTH_REGEX = re.compile(r'strokeWidth=(\d+)')


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


class DrawioBackground:
    """Collects a .svg and the corresponding .drawio XML file together,
    provides useful accessor methods for both."""

    raster_background: tk.PhotoImage

    def __init__(self, png_path: Path, xml_path: Path):
        self._png_path = png_path
        self._xml_path = xml_path
        self._widget_text_to_coords: Dict[str, Coords] = {}

        self.raster_background = tk.PhotoImage(file=self._png_path)

        # Build an index of each mxCell, where a widget is, and the name of the
        # widget there. Normally we would just search for the text of the
        # widget directly, but any formatting or extra whitespaces in the XML's
        # conception of the widget name will break this. Specifically, I would
        # try to match "High-Voltage Habitat Bus" on
        # value="&lt;div style=&quot;font-size: 12px;&quot;&gt;High-Voltage Habitat Bus&lt;br style=&quot;font-size: 12px;&quot;&gt;&lt;/div&gt;"
        # and fail.
        xml_tree = ET.parse(xml_path).getroot()
        for mxCell in xml_tree.findall('.//mxCell'):
            if 'value' not in mxCell.attrib:
                continue
            raw_widget_text = mxCell.attrib['value']
            if raw_widget_text == '':
                continue
            no_html_widget_text = re.sub(r'<.+?>', '', raw_widget_text)
            widget_text = re.sub(r'\s+', ' ', no_html_widget_text.strip())
            widget_text_normalized = widget_text.lower()

            mxGeometry = mxCell.find('./mxGeometry')
            if mxGeometry is None:
                log.error(f"Couldn't find mxGeometry for {widget_text_normalized}!")
                continue
            try:
                x = round(float(mxGeometry.attrib['x']))
                y = round(float(mxGeometry.attrib['y']))
                width = round(float(mxGeometry.attrib['width']))
                height = round(float(mxGeometry.attrib['height']))
                border_match = BORDER_WIDTH_REGEX.search(mxCell.attrib['style'])
                if border_match:
                    border = round(float(border_match.group(1)))
                else:
                    border = 2
            except KeyError:
                log.error(f"Couldn't find x/y/width/height for {widget_text_normalized}!")
                continue

            log.debug(f"Found {widget_text_normalized} at {x}+{width}, {y}+{height}.")
            coords = Coords(x=x, y=y, width=width + border * 2, height=height + border * 2)

            assert widget_text_normalized not in self._widget_text_to_coords, \
                f"Found unexpected duplicate widget in drawio diagram: {widget_text_normalized}!"
            self._widget_text_to_coords[widget_text_normalized] = coords

    def widget_coords(self, widget_text: str) -> Coords:
        try:
            return self._widget_text_to_coords[widget_text.lower()]
        except KeyError:
            log.error(f"Didn't find {widget_text.lower()} with corresponding x, y, width, and height in the drawio diagram!")
            raise


class DetailsFrame(ttk.Frame, Redrawable):
    """
    Displays information about the currently-selected component in
    the bottom left of the window.

    Most fields are common to all components (name, description, current,
    etc.), but some components might have a unique field or two (rad
    shield setting, reactor status).
    """

    def __init__(self, parent: ttk.Widget):
        ttk.Frame.__init__(self, parent)
        Redrawable.__init__(self)


class WarningsFrame(ttk.Frame, Redrawable):
    """
    Displays a list of warnings in a frame at the bottom of the window,
    next to DetailsFrame.
    """

    def __init__(self, parent: ttk.Widget):
        ttk.Frame.__init__(self, parent)
        Redrawable.__init__(self)


class CoolantSection():
    """
    Contains two coolant buttons horizontally side by side. Places these coolant
    buttons on a given row inside a widget.
    """

    def __init__(self, parent: ttk.Widget, component_n: int, coords: Coords):
        self._lp1 = CoolantButton(parent, component_n, 0)
        self._lp1.grid(row=row_n, column=0)
        self._lp2 = CoolantButton(parent, component_n, 1)
        self._lp2.grid(row=row_n, column=1)


class CoolantButton(ttk.Button, Redrawable):
    """
    A component will own this button. Clicking this button will send a request
    to hook up a component to a certain coolant loop.
    """

    def __init__(self, parent: ttk.Widget, component_n: int, coolant_n: int):
        """
        @parent: The ComponentBlock that owns this CoolantButton.
        @component_n: The index of the component that owns this.
        @coolant_n: The number [0-2] corresponding to the coolant loop.
                    Coolant 0 is the first Hab coolant loop, and coolant 2 is
                    AYSE loop.
        """
        coolant_loop_texts = ['❄1', '❄2', '❄']

        ttk.Button.__init__(self, parent, text=coolant_loop_texts[coolant_n], command=self._onpress)
        Redrawable.__init__(self)

        self._component_n = component_n
        self._coolant_n = coolant_n

    def _onpress(self):
        hab_eng.push_command(
            Request(ident=Request.TOGGLE_COMPONENT_COOLANT,
                    component_to_loop=Request.ComponentToLoop(component=self._component_n, loop=self._coolant_n)))

        if self.instate(['pressed']):
            self.state(['!pressed'])
        else:
            self.state(['pressed'])

    def redraw(self, state: EngineeringState):

        component = state.components[self._component_n]
        if state.coolant_loops[self._coolant_n] in component.connected_coolant_loops():
            self.state(['pressed'])
        else:
            self.state(['!pressed'])


class SimpleText(Redrawable):
    """
    Redrawable of a simple box, with the inner text controlled by a StringVar

    Args:
        parent (ttk.Widget): Required by tkinter, the parent widget that this is created in.
        inner_text (tk.StringVar or str): The initial text in the widget (a str will be converted to a StringVar)
        coords (Coords): the x, y, width, and height of the widget

    Attributes:
        stringvar (tk.StringVar): Update this to change the text of the widget
    """

    _stringvar: tk.StringVar
    _text_generator: Callable[[EngineeringState], str]


    def __init__(self, parent: ttk.Widget, background: DrawioBackground, component_name: str, text_function: Callable[[EngineeringState], str]):
        coords = background.widget_coords(component_name)
        self._stringvar = tk.StringVar()
        self._frame = ttk.Frame(parent)
        self._frame.place(x=coords.x, y=coords.y, width=coords.width, height=coords.height)
        super().__init__()

        # Add the text area
        self._label = ttk.Label(
            self._frame, textvariable=self._stringvar,
            justify=tk.CENTER, anchor=tk.CENTER, wraplength=coords.width - INNER_TEXT_MARGIN
        )
        self._text_generator = text_function

        # Pack coolant buttons around the text area
        self._coolant_button_0 = CoolantButton(self._frame, component_n=strings.COMPONENT_NAMES.index(component_name), coolant_n=0)

        self._label.pack(side=tk.TOP, expand=True, fill=tk.BOTH)
        self._coolant_button_0.pack(side=tk.LEFT)

    def redraw(self, state: EngineeringState):
        self._stringvar.set(self._text_generator(state))


class RCONFrame(SimpleText):
    """
    Visually represents a component, such as RCON1.
    """

    def __init__(self,
                 parent: ttk.Widget,
                 background: DrawioBackground,
                 component_name: str,
                 text_function: Callable[[EngineeringState], str],
                 has_coolant_controls: bool = True):
        """
        @parent: The GridPage that this will be placed in
        @optional_text: Optional. An EngineeringState->str function, this RCONFrame will reserve
                        a line of text for the output of the function and keep it updated each tick.
        @x: The x position of the top-left corner.
        @y: The y position of the top-left corner.
        """
        SimpleText.__init__(self, parent=parent, background=background, component_name=component_name, text_function=text_function)

        self._optional_text_value = tk.StringVar()
        ttk.Label(parent, textvariable=self._optional_text_value).grid(row=0, column=0)

        self._temperature_text = tk.StringVar()
        ttk.Label(parent, textvariable=self._temperature_text).grid(row=0, column=1)


class EngineFrame(SimpleText):

    def __init__(self, parent: ttk.Widget, background: DrawioBackground, component_name: str, text_function: Callable[[EngineeringState], str]):
        super().__init__(parent, background, component_name, text_function)


class RadShieldFrame(SimpleText):

    def __init__(self, parent: ttk.Widget, background: DrawioBackground, component_name: str, text_function: Callable[[EngineeringState], str]):
        super().__init__(parent, background, component_name, text_function)

        # Grid used instead of packing to organize widgets for formatting purposes
        ttk.Button(parent, text="SET").grid(row=1, column=0)
        ttk.Entry(parent, width=5).grid(row=1, column=1)
