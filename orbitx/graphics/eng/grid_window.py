from pathlib import Path
from PIL import Image, ImageTk
import tkinter as tk


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
        grid_background = ImageTk.PhotoImage(Image.open(Path('data', 'powergrid-background.png')))
        bg_label = tk.Label(self, image=grid_background)
        bg_label.image = grid_background
        bg_label.place(x=0, y=0)


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
