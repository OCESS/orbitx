from datetime import datetime
from pathlib import Path
from PIL import Image, ImageTk
from typing import Optional, Callable
import tkinter as tk

from orbitx.strings import LP1, LP2, ACC1
from orbitx.data_structures import EngineeringState


class GridPage(tk.Frame):
    """
    Contains the power grid, i.e. all components and power buses.
    Also contains component detail and temperature warning frames.

    Uses a fixed layout engine, with a raster image as a background.
    We could use a gridding engine and make a responsive design, but
    that's a _lot_ more work and isn't a priority.
    """

    def __init__(self, parent: tk.Widget):
        tk.Frame.__init__(self, parent)

        # Load a background image. If the image is any larger than the window's
        # dimensions, the extra will be cut off.
        grid_background = ImageTk.PhotoImage(
            Image.open(Path('data', 'powergrid-background.png')))
        bg_label = tk.Label(self, image=grid_background)
        bg_label.image = grid_background
        bg_label.place(x=0, y=0)

        self.blah = ComponentBlock(self, ACC1, x=5, y=5)


class DetailsFrame(tk.Frame):
    """
    Displays information about the currently-selected component in
    the bottom left of the window.

    Most fields are common to all components (name, description, current,
    etc.), but some components might have a unique field or two (rad
    shield setting, reactor status).
    """

    def __init__(self, parent: tk.Widget):
        super().__init__(self, parent)


class WarningsFrame(tk.Frame):
    """
    Displays a list of warnings in a frame at the bottom of the window,
    next to DetailsFrame.
    """

    def __init__(self, parent: tk.Widget):
        super().__init__(self, parent)


class ComponentBlock(tk.LabelFrame):
    """
    Visually represents a component, such as RCON1.
    """

    def __init__(
        self,
        parent: GridPage,
        component_name: str,
        optional_text: Optional[Callable[[EngineeringState], str]] = None,
        has_coolant_controls: bool = True, *,
        x: int, y: int
    ):
        """
        @parent: The GridPage that this will be placed in
        @optional_text: Optional. An EngineeringState->str function, this ComponentBlock will reserve
                        a line of text for the output of the function and keep it updated each tick.
        @x: The x position of the top-left corner.
        @y: The y position of the top-left corner.
        """
        tk.LabelFrame.__init__(self, parent, text=component_name, labelanchor=tk.N)
        self.place(x=x, y=y)

        self._component_name = component_name

        self._optional_text_generator = optional_text
        self._optional_text_value = tk.StringVar()
        tk.Label(self, textvariable=self._optional_text_value).pack(side=tk.TOP)

        self._temperature_text = tk.StringVar()
        tk.Label(self, textvariable=self._temperature_text).pack(side=tk.TOP)

        tk.Button(self, text=LP1).pack(fill=tk.X, expand=True, side=tk.LEFT)
        tk.Button(self, text=LP2).pack(fill=tk.X, expand=True, side=tk.RIGHT)

    def redraw(self, state: EngineeringState):
        if self._optional_text_generator is not None:
            self._optional_text_value.set(self._optional_text_generator(
                state))

        self._temperature_text.set(state.components[self._component_name].temperature)
