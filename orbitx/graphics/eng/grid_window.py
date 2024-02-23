import re
import logging
import tkinter as tk
from pathlib import Path
import xml.etree.ElementTree as ET
from typing import Dict

from orbitx import strings
from orbitx.graphics.eng import tkinter_widgets as widgets

log = logging.getLogger('orbitx')

BORDER_WIDTH_REGEX = re.compile(r'strokeWidth=(\d+)')


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
        png_path = Path('data', 'engineering', 'orbitx-powergrid.drawio.png')
        drawio_xml_path = Path('data', 'engineering', 'orbitx-powergrid.drawio')
        background = DrawioBackground(png_path, drawio_xml_path)
        bg_label = tk.Label(self, image=background.raster_background)
        bg_label.image = background.raster_background
        bg_label.place(x=0, y=0)

        """ Primary Habitat Bus Widgets """
        widgets.SimpleText(self, coords=background.widget_coords(strings.HAB_REACT), text_function=lambda state:
            f"{strings.HAB_REACT}\n"
            f"Status: {'Online' if state.components[strings.HAB_REACT].connected else 'Offline'}\n"
            f"Temperature: {state.components[strings.HAB_REACT].temperature:,} %"
        )
        widgets.SimpleText(self, coords=background.widget_coords(strings.HAB_FUEL), text_function=lambda state:
            f"{strings.HAB_FUEL}\n"
            f"{state.habitat_fuel:,} kg"
        )
        widgets.RCONFrame(self, background.widget_coords(strings.RCON1), lambda x: f"{strings.RCON1} Current")
        widgets.RCONFrame(self, background.widget_coords(strings.RCON2), lambda x: f"{strings.RCON1} Current")
        widgets.RadShieldFrame(self, strings.RADS1, coords=background.widget_coords(strings.RADS1))
        widgets.RadShieldFrame(self, strings.RADS2, coords=background.widget_coords(strings.RADS2))
        widgets.SimpleText(self, coords=background.widget_coords(strings.RADAR), text_function=lambda _: strings.RADAR)
        widgets.SimpleText(self, coords=background.widget_coords(strings.RCSP), text_function=lambda _: strings.RCSP)
        widgets.SimpleText(self, coords=background.widget_coords(strings.AGRAV), text_function=lambda _: strings.AGRAV)
        widgets.SimpleText(self, coords=background.widget_coords(strings.RADAR), text_function=lambda _: strings.RADAR)

        widgets.EngineFrame(self, coords=background.widget_coords(strings.ACC1), text_function=lambda _: strings.ACC1)
        widgets.EngineFrame(self, coords=background.widget_coords(strings.ACC2), text_function=lambda _: strings.ACC2)
        widgets.EngineFrame(self, coords=background.widget_coords(strings.ACC3), text_function=lambda _: strings.ACC3)
        widgets.EngineFrame(self, coords=background.widget_coords(strings.ACC4), text_function=lambda _: strings.ACC4)
        widgets.EngineFrame(self, coords=background.widget_coords(strings.ION1), text_function=lambda _: strings.ION1)
        widgets.EngineFrame(self, coords=background.widget_coords(strings.ION2), text_function=lambda _: strings.ION2)
        widgets.EngineFrame(self, coords=background.widget_coords(strings.ION3), text_function=lambda _: strings.ION3)
        widgets.EngineFrame(self, coords=background.widget_coords(strings.ION4), text_function=lambda _: strings.ION4)

        """ Secondary Habitat Bus Widgets """
        widgets.SimpleText(self, coords=background.widget_coords(strings.BAT1), text_function=lambda _: strings.BAT1)
        widgets.SimpleText(self, coords=background.widget_coords(strings.FCELL), text_function=lambda _: strings.FCELL)
        widgets.SimpleText(self, coords=background.widget_coords(strings.COM), text_function=lambda _: strings.COM)

        """ Tertiary Habitat Bus Widgets """
        widgets.SimpleText(self, coords=background.widget_coords(strings.INS), text_function=lambda _: strings.INS)
        widgets.SimpleText(self, coords=background.widget_coords(strings.LOS), text_function=lambda _: strings.LOS)
        widgets.SimpleText(self, coords=background.widget_coords(strings.GNC), text_function=lambda _: strings.GNC)
        widgets.SimpleText(self, coords=background.widget_coords(strings.BAT2), text_function=lambda _: strings.BAT2)
        widgets.SimpleText(self, coords=background.widget_coords(strings.EECOM), text_function=lambda _: strings.EECOM)
        widgets.SimpleText(self, coords=background.widget_coords(strings.NETWORK), text_function=lambda _: strings.NETWORK)

        """ Ayse Power Bus Widgets """
        widgets.PowerBusFrame(self, strings.AYSE_BUS, coords=background.widget_coords(strings.AYSE_BUS))
        widgets.SimpleText(self, coords=background.widget_coords(strings.AYSE_BAT), text_function=lambda _: strings.AYSE_BAT)

        widgets.RCONFrame(self, coords=background.widget_coords(strings.ARCON1), text_function=lambda _: strings.ARCON1)
        widgets.RCONFrame(self, coords=background.widget_coords(strings.ARCON2), text_function=lambda _: strings.ARCON2)
        widgets.SimpleText(self, coords=background.widget_coords(strings.AYSE_REACT), text_function=lambda state:
            f"{strings.AYSE_REACT}\n"
            f"Status: {'Online' if state.components[strings.AYSE_REACT].connected else 'Offline'}\n"
            f"Temperature: {state.components[strings.AYSE_REACT].temperature:,} %\n"
            f"Voltage: {state.components.Electricals()[strings.AYSE_REACT].voltage:,} V"
        )


class DrawioBackground:
    """Collects a .svg and the corresponding .drawio XML file together,
    provides useful accessor methods for both."""

    raster_background: tk.PhotoImage

    def __init__(self, png_path: Path, xml_path: Path):
        self._png_path = png_path
        self._xml_path = xml_path
        self._widget_text_to_coords: Dict[str, widgets.Coords] = {}

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
            coords = widgets.Coords(x=x, y=y, width=width + border * 2, height=height + border * 2)

            assert widget_text_normalized not in self._widget_text_to_coords, \
                f"Found unexpected duplicate widget in drawio diagram: {widget_text_normalized}!"
            self._widget_text_to_coords[widget_text_normalized] = coords

    def widget_coords(self, widget_text: str) -> widgets.Coords:
        try:
            return self._widget_text_to_coords[widget_text.lower()]
        except KeyError:
            log.error(f"Didn't find {widget_text.lower()} with corresponding x, y, width, and height in the drawio diagram!")
            raise
