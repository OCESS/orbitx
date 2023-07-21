import tkinter as tk
import tksvg
from pathlib import Path
import xml.etree.ElementTree as ET

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
        svg_path = Path('data', 'engineering', 'orbitx-powergrid.svg')
        grid_background = tksvg.SvgImage(file=svg_path)
        bg_label = tk.Label(self, image=grid_background)
        bg_label.image = grid_background
        bg_label.place(x=0, y=0)

        svg_tree = ET.parse(svg_path).getroot()

        """ Primary Habitat Bus Widgets """
        widgets.PowerBusFrame(self, strings.BUS1, svg_tree=svg_tree)

        widgets.ReactorFrame(self, strings.HAB_REACT, svg_tree=svg_tree)
        widgets.FuelFrame(self, strings.HAB_FUEL, svg_tree=svg_tree)
        widgets.RCONFrame(self, strings.RCON1, lambda x: "Current", svg_tree=svg_tree)
        widgets.RCONFrame(self, strings.RCON2, lambda x: "Current", svg_tree=svg_tree)
        widgets.RadShieldFrame(self, strings.RADS1, svg_tree=svg_tree)
        widgets.RadShieldFrame(self, strings.RADS2, svg_tree=svg_tree)
        widgets.SimpleFrame(self, strings.RADAR, svg_tree=svg_tree)
        widgets.SimpleFrame(self, strings.RCSP, svg_tree=svg_tree)
        widgets.SimpleFrame(self, strings.AGRAV, svg_tree=svg_tree)

        widgets.EngineFrame(self, strings.ACC1, svg_tree=svg_tree)
        widgets.EngineFrame(self, strings.ACC2, svg_tree=svg_tree)
        widgets.EngineFrame(self, strings.ACC3, svg_tree=svg_tree)
        widgets.EngineFrame(self, strings.ACC4, svg_tree=svg_tree)
        widgets.EngineFrame(self, strings.ION1, svg_tree=svg_tree)
        widgets.EngineFrame(self, strings.ION2, svg_tree=svg_tree)
        widgets.EngineFrame(self, strings.ION3, svg_tree=svg_tree)
        widgets.EngineFrame(self, strings.ION4, svg_tree=svg_tree)

        """ Secondary Habitat Bus Widgets """
        widgets.PowerBusFrame(self, strings.BUS2, svg_tree=svg_tree)

        widgets.BatteryFrame(self, strings.BAT1, svg_tree=svg_tree)
        widgets.SimpleFrame(self, strings.FCELL, svg_tree=svg_tree)
        widgets.SimpleFrame(self, strings.COM, svg_tree=svg_tree)

        """ Tertiary Habitat Bus Widgets """
        widgets.SimpleFrame(self, strings.INS, svg_tree=svg_tree)
        widgets.SimpleFrame(self, strings.LOS, svg_tree=svg_tree)
        widgets.SimpleFrame(self, strings.GNC, svg_tree=svg_tree)
        widgets.BatteryFrame(self, strings.BAT2, svg_tree=svg_tree)
        widgets.SimpleFrame(self, strings.EECOM, svg_tree=svg_tree)
        widgets.SimpleFrame(self, strings.NETWORK, svg_tree=svg_tree)

        """ Ayse Power Bus Widgets """
        widgets.PowerBusFrame(self, strings.AYSE_BUS, svg_tree=svg_tree)

        widgets.RCONFrame(self, strings.ARCON1, lambda x: "Current", svg_tree=svg_tree)
        widgets.RCONFrame(self, strings.ARCON2, lambda x: "Current", svg_tree=svg_tree)
        widgets.ReactorFrame(self, strings.AYSE_REACT, svg_tree=svg_tree)
