import re
import logging
import tkinter as tk
import tksvg
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
        svg_path = Path('data', 'engineering', 'orbitx-powergrid.svg')
        drawio_xml_path = Path('data', 'engineering', 'orbitx-powergrid.drawio')
        drawio_svg = DrawioSvgBackground(svg_path, drawio_xml_path)
        grid_background = drawio_svg.svg_image()
        bg_label = tk.Label(self, image=grid_background)
        bg_label.image = grid_background
        bg_label.place(x=0, y=0)

        """ Primary Habitat Bus Widgets """
        widgets.PowerBusFrame(self, strings.BUS1, coords=drawio_svg.widget_coords(strings.BUS1))
        widgets.ReactorFrame(self, strings.HAB_REACT, coords=drawio_svg.widget_coords(strings.HAB_REACT))
        widgets.FuelFrame(self, strings.HAB_FUEL, coords=drawio_svg.widget_coords(strings.HAB_FUEL))
        widgets.RCONFrame(self, strings.RCON1, lambda x: "Current", coords=drawio_svg.widget_coords(strings.RCON1))
        widgets.RCONFrame(self, strings.RCON2, lambda x: "Current", coords=drawio_svg.widget_coords(strings.RCON2))
        widgets.RadShieldFrame(self, strings.RADS1, coords=drawio_svg.widget_coords(strings.RADS1))
        widgets.RadShieldFrame(self, strings.RADS2, coords=drawio_svg.widget_coords(strings.RADS2))
        widgets.SimpleFrame(self, strings.RADAR, coords=drawio_svg.widget_coords(strings.RADAR))
        widgets.SimpleFrame(self, strings.RCSP, coords=drawio_svg.widget_coords(strings.RCSP))
        widgets.SimpleFrame(self, strings.AGRAV, coords=drawio_svg.widget_coords(strings.AGRAV))

        widgets.EngineFrame(self, strings.ACC1, coords=drawio_svg.widget_coords(strings.ACC1))
        widgets.EngineFrame(self, strings.ACC2, coords=drawio_svg.widget_coords(strings.ACC2))
        widgets.EngineFrame(self, strings.ACC3, coords=drawio_svg.widget_coords(strings.ACC3))
        widgets.EngineFrame(self, strings.ACC4, coords=drawio_svg.widget_coords(strings.ACC4))
        widgets.EngineFrame(self, strings.ION1, coords=drawio_svg.widget_coords(strings.ION1))
        widgets.EngineFrame(self, strings.ION2, coords=drawio_svg.widget_coords(strings.ION2))
        widgets.EngineFrame(self, strings.ION3, coords=drawio_svg.widget_coords(strings.ION3))
        widgets.EngineFrame(self, strings.ION4, coords=drawio_svg.widget_coords(strings.ION4))

        """ Secondary Habitat Bus Widgets """
        widgets.PowerBusFrame(self, strings.BUS2, coords=drawio_svg.widget_coords(strings.BUS2))

        widgets.BatteryFrame(self, strings.BAT1, coords=drawio_svg.widget_coords(strings.BAT1))
        widgets.SimpleFrame(self, strings.FCELL, coords=drawio_svg.widget_coords(strings.FCELL))
        widgets.SimpleFrame(self, strings.COM, coords=drawio_svg.widget_coords(strings.COM))

        """ Tertiary Habitat Bus Widgets """
        widgets.SimpleFrame(self, strings.INS, coords=drawio_svg.widget_coords(strings.INS))
        widgets.SimpleFrame(self, strings.LOS, coords=drawio_svg.widget_coords(strings.LOS))
        widgets.SimpleFrame(self, strings.GNC, coords=drawio_svg.widget_coords(strings.GNC))
        widgets.BatteryFrame(self, strings.BAT2, coords=drawio_svg.widget_coords(strings.BAT2))
        widgets.SimpleFrame(self, strings.EECOM, coords=drawio_svg.widget_coords(strings.EECOM))
        widgets.SimpleFrame(self, strings.NETWORK, coords=drawio_svg.widget_coords(strings.NETWORK))

        """ Ayse Power Bus Widgets """
        widgets.PowerBusFrame(self, strings.AYSE_BUS, coords=drawio_svg.widget_coords(strings.AYSE_BUS))

        widgets.RCONFrame(self, strings.ARCON1, lambda x: "Current", coords=drawio_svg.widget_coords(strings.ARCON1))
        widgets.RCONFrame(self, strings.ARCON2, lambda x: "Current", coords=drawio_svg.widget_coords(strings.ARCON2))
        widgets.ReactorFrame(self, strings.AYSE_REACT, coords=drawio_svg.widget_coords(strings.AYSE_REACT))


class DrawioSvgBackground:
    """Collects a .svg and the corresponding .drawio XML file together,
    provides useful accessor methods for both."""

    def __init__(self, svg_path: Path, xml_path: Path):
        self._svg_path = svg_path
        self._xml_path = xml_path
        self._widget_text_to_coords: Dict[str, widgets.Coords] = {}

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

            mxGeometry = mxCell.find('./mxGeometry')
            if mxGeometry is None:
                log.error(f"Couldn't find mxGeometry for {widget_text}!")
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
                log.error(f"Couldn't find x/y/width/height for {widget_text}!")
                continue

            log.debug(f"Found {widget_text} at {x}+{width}, {y}+{height}.")
            coords = widgets.Coords(x=x, y=y, width=width + border * 2, height=height + border * 2)

            assert widget_text not in self._widget_text_to_coords, \
                f"Found unexpected duplicate widget in drawio diagram: {widget_text}!"
            self._widget_text_to_coords[widget_text] = coords

    def svg_image(self) -> tksvg.SvgImage:
        return tksvg.SvgImage(file=self._svg_path)

    def widget_coords(self, widget_text: str) -> widgets.Coords:
        try:
            return self._widget_text_to_coords[widget_text]
        except KeyError:
            log.error(f"Didn't find {widget_text} with corresponding x, y, width, and height in the drawio diagram!")
            raise
