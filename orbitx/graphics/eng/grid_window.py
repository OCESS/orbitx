import tkinter as tk
from PIL import Image, ImageTk
from pathlib import Path

from orbitx import strings
from orbitx.graphics.eng import tkinter_widgets as widgets


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
            Image.open(Path('data', 'engineering', 'powergrid-background.png')))
        bg_label = tk.Label(self, image=grid_background)
        bg_label.image = grid_background
        bg_label.place(x=0, y=0)

        widgets.ComponentConnection.load_glyphs()

        widgets.ComponentBlock(self, strings.ACC1, x=5, y=5)
        widgets.ComponentConnection(self, strings.ACC1, x=5, y=50)
        widgets.ComponentBlock(self, strings.RCON1, x=220, y=95)
        widgets.ComponentBlock(self,  strings.RCON2, x=345, y=95)
        widgets.RadShield(self, x=495, y=95)
        widgets.FuelFrame(self, x=100, y=100)