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
        bg_label.image = grid_background  # TODO: does this do anything? Label has no image attribute
        bg_label.place(x=0, y=0)

        widgets.ComponentConnection.load_glyphs()

#        widgets.ComponentConnection(self, strings.ACC1, x=5, y=50)

        """ Primary Habitat Bus Widgets """
        widgets.PowerBusFrame(self, strings.BUS1, x=325, y=325)

        widgets.ReactorFrame(self, strings.HAB_REACT, x=75, y=275)
        widgets.FuelFrame(self, x=75, y=100)
        widgets.RCONFrame(self, strings.RCON1, lambda x: "Current", x=220, y=95)
        widgets.RCONFrame(self,  strings.RCON2, lambda x: "Current", x=345, y=95)
        widgets.RadShieldFrame(self, x=495, y=95)
        widgets.SimpleFrame(self, strings.RADAR, x=650, y=160)
        widgets.SimpleFrame(self, strings.RCSP, x=730, y=160)
        widgets.AGRAVFrame(self, x=815, y=95)
        widgets.EngineControlFrame(self, "Engine Ionizers", True, x=910, y=10)
        widgets.EngineControlFrame(self, "Engine Accelerators", False, x=1080, y=10)

        """ Secondary Habitat Bus Widgets """
        widgets.PowerBusFrame(self, strings.BUS2, x=60, y=500)

        widgets.BatteryFrame(self, x=230, y=610)
        widgets.SimpleFrame(self, "Fuel Cell", x=45, y=600)
        widgets.SimpleFrame(self, strings.COM, x=80, y=400)

        """ Tertiary Habitat Bus Widgets """
        widgets.SimpleFrame(self, strings.INS, x=465, y=400)
        widgets.SimpleFrame(self, strings.LOS, x=515, y=400)
        widgets.SimpleFrame(self, strings.GNC, x=565, y=400)
        widgets.BatteryFrame(self, x=650, y=400)
        widgets.SimpleFrame(self, strings.EECOM, x=750, y=480)
        widgets.SimpleFrame(self, strings.NETWORK, x=750, y=530)

        """ Ayse Power Bus Widgets """
        widgets.PowerBusFrame(self, strings.AYSE_BUS, x=1040, y=640)

        widgets.EngineFrame(self, x=1080, y=850)
        widgets.RCONFrame(self, strings.ARCON1, lambda x: "Current", x=830, y=730)
        widgets.RCONFrame(self, strings.ARCON2, lambda x: "Current", x=830, y=620)
        widgets.ReactorFrame(self, strings.AYSE_REACT, x=980, y=460)
