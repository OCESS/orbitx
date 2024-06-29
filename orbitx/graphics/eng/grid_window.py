import logging
import tkinter.ttk as ttk
from pathlib import Path
import sv_ttk

from orbitx import strings
from orbitx.graphics.eng import tkinter_widgets as widgets

log = logging.getLogger('orbitx')


class GridPage(ttk.Frame):
    """
    Contains the power grid, i.e. all components and power buses.
    Also contains component detail and temperature warning frames.

    Uses a fixed layout engine, with a raster image as a background.
    We could use a gridding engine and make a responsive design, but
    that's a _lot_ more work and isn't a priority.
    """

    def __init__(self, parent: ttk.Widget):
        ttk.Frame.__init__(self, parent)

        # Load a background image. If the image is any larger than the window's
        # dimensions, the extra will be cut off.
        png_path = Path('data', 'engineering', 'orbitx-powergrid.drawio.png')
        drawio_xml_path = Path('data', 'engineering', 'orbitx-powergrid.drawio')
        background = widgets.DrawioBackground(png_path, drawio_xml_path)
        bg_label = ttk.Label(self, image=background.raster_background)
        bg_label.image = background.raster_background
        bg_label.place(x=0, y=0)

        """ Primary Habitat Bus Widgets """
        widgets.SimpleText(self, background=background, component_name=strings.HAB_REACT, text_function=lambda state:
            f"{strings.HAB_REACT}\n"
            f"Status: {'Online' if state.components[strings.HAB_REACT].connected else 'Offline'}\n"
            f"Temperature: {state.components[strings.HAB_REACT].temperature:,} %"
        )
        # widgets.SimpleText(self, background=background, component_name=strings.HAB_FUEL, text_function=lambda state:
        #     f"{strings.HAB_FUEL}\n"
        #     f"{state.habitat_fuel:,} kg"
        # )
        widgets.RCONFrame(self, background=background, component_name=strings.RCON1)
        widgets.RCONFrame(self, background=background, component_name=strings.RCON2)
        widgets.RadShieldFrame(self, background=background, component_name=strings.RADS1, text_function=lambda state: f"{state.rad_shield_percentage:,} %")
        widgets.RadShieldFrame(self, background=background, component_name=strings.RADS2, text_function=lambda state: f"{state.rad_shield_percentage:,} %")
        widgets.SimpleText(self, background=background, component_name=strings.RADAR, text_function=lambda _: strings.RADAR)
        widgets.SimpleText(self, background=background, component_name=strings.RCSP, text_function=lambda _: strings.RCSP)
        widgets.SimpleText(self, background=background, component_name=strings.AGRAV, text_function=lambda _: strings.AGRAV)
        widgets.SimpleText(self, background=background, component_name=strings.RADAR, text_function=lambda _: strings.RADAR)
        widgets.SimpleText(self, background=background, component_name=strings.FCELL_INJ, text_function=lambda _: strings.FCELL_INJ)
        widgets.SimpleText(self, background=background, component_name=strings.REACT_INJ1, text_function=lambda _: strings.REACT_INJ1)
        widgets.SimpleText(self, background=background, component_name=strings.REACT_INJ2, text_function=lambda _: strings.REACT_INJ2)
        widgets.SimpleText(self, background=background, component_name=strings.ENGINE_INJ1, text_function=lambda _: strings.ENGINE_INJ1)
        widgets.SimpleText(self, background=background, component_name=strings.ENGINE_INJ2, text_function=lambda _: strings.ENGINE_INJ2)
        widgets.SimpleText(self, background=background, component_name=strings.PRIMARY_PUMP_1, text_function=lambda _: strings.PRIMARY_PUMP_1)
        widgets.SimpleText(self, background=background, component_name=strings.PRIMARY_PUMP_2, text_function=lambda _: strings.PRIMARY_PUMP_2)

        widgets.EngineFrame(self, background=background, component_name=strings.ACC1, text_function=lambda _: strings.ACC1)
        widgets.EngineFrame(self, background=background, component_name=strings.ACC2, text_function=lambda _: strings.ACC2)
        widgets.EngineFrame(self, background=background, component_name=strings.ACC3, text_function=lambda _: strings.ACC3)
        widgets.EngineFrame(self, background=background, component_name=strings.ACC4, text_function=lambda _: strings.ACC4)
        widgets.EngineFrame(self, background=background, component_name=strings.ION1, text_function=lambda _: strings.ION1)
        widgets.EngineFrame(self, background=background, component_name=strings.ION2, text_function=lambda _: strings.ION2)
        widgets.EngineFrame(self, background=background, component_name=strings.ION3, text_function=lambda _: strings.ION3)
        widgets.EngineFrame(self, background=background, component_name=strings.ION4, text_function=lambda _: strings.ION4)

        widgets.SimpleText(self, background=background, component_name=strings.HAB_CONV, text_function=lambda _: strings.HAB_CONV)

        """ Secondary Habitat Bus Widgets """
        widgets.SimpleText(self, background=background, component_name=strings.BAT1, text_function=lambda _: strings.BAT1)
        widgets.SimpleText(self, background=background, component_name=strings.FCELL, text_function=lambda _: strings.FCELL)
        widgets.SimpleText(self, background=background, component_name=strings.COM, text_function=lambda _: strings.COM)
        widgets.SimpleText(self, background=background, component_name=strings.SECONDARY_PUMP_1, text_function=lambda _: strings.SECONDARY_PUMP_1)
        widgets.SimpleText(self, background=background, component_name=strings.SECONDARY_PUMP_2, text_function=lambda _: strings.SECONDARY_PUMP_2)
        widgets.SimpleText(self, background=background, component_name=strings.REACTOR_HEATER, text_function=lambda _: strings.REACTOR_HEATER)

        """ Tertiary Habitat Bus Widgets """
        widgets.SimpleText(self, background=background, component_name=strings.INS, text_function=lambda _: strings.INS)
        widgets.SimpleText(self, background=background, component_name=strings.LOS, text_function=lambda _: strings.LOS)
        widgets.SimpleText(self, background=background, component_name=strings.GNC, text_function=lambda _: strings.GNC)
        widgets.SimpleText(self, background=background, component_name=strings.BAT2, text_function=lambda _: strings.BAT2)
        widgets.SimpleText(self, background=background, component_name=strings.EECOM, text_function=lambda _: strings.EECOM)
        widgets.SimpleText(self, background=background, component_name=strings.NETWORK, text_function=lambda _: strings.NETWORK)

        """ Ayse Power Bus Widgets """
        widgets.SimpleText(self, background=background, component_name=strings.AYSE_CONV, text_function=lambda _: strings.AYSE_CONV)
        widgets.SimpleText(self, background=background, component_name=strings.AYSE_BAT, text_function=lambda _: strings.AYSE_BAT)
        widgets.SimpleText(self, background=background, component_name=strings.GPD1, text_function=lambda _: strings.GPD1)
        widgets.SimpleText(self, background=background, component_name=strings.GPD2, text_function=lambda _: strings.GPD2)
        widgets.SimpleText(self, background=background, component_name=strings.GPD3, text_function=lambda _: strings.GPD3)
        widgets.SimpleText(self, background=background, component_name=strings.GPD4, text_function=lambda _: strings.GPD4)
        widgets.SimpleText(self, background=background, component_name=strings.TTC, text_function=lambda _: strings.TTC)
        widgets.SimpleText(self, background=background, component_name=strings.AYSE_PUMP_1, text_function=lambda _: strings.AYSE_PUMP_1)
        widgets.SimpleText(self, background=background, component_name=strings.AYSE_PUMP_2, text_function=lambda _: strings.AYSE_PUMP_2)

        widgets.RCONFrame(self, background=background, component_name=strings.ARCON1)
        widgets.RCONFrame(self, background=background, component_name=strings.ARCON2)
        widgets.SimpleText(self, background=background, component_name=strings.AYSE_REACT, text_function=lambda state:
            f"{strings.AYSE_REACT}\n"
            f"Status: {'Online' if state.components[strings.AYSE_REACT].connected else 'Offline'}\n"
            f"Temperature: {state.components[strings.AYSE_REACT].temperature:,} %\n"
            f"Voltage: {state.components.Electricals()[strings.AYSE_REACT].voltage:,} V"
        )

        # sv_ttk.set_theme("light")
