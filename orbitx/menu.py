from typing import List, Callable
import orbitx.calculator as calc
from . import state
import orbitx.style as style        # HTML5, Javascript and CSS3 code for UI
import numpy as np

import vpython

DEFAULT_CENTRE = 'Habitat'
DEFAULT_REFERENCE = 'Earth'
DEFAULT_TARGET = 'Moon'


class Menu:
    def __init__(self):
        self.reference: state.Entity = None
        self.target: state.Entity = None
        self.habitat: state.Entity = None
    # end of __init__

    def _update_RTH(self, gui):
        self.reference = gui.get_reference()
        self.target = gui.get_target()
        self.habitat = gui.get_habitat()
    # end of _update_RTH

    def set_caption(self, gui) -> None:
        """Set and update the captions."""

        # There's a bit of magic here. Normally, vpython.wtext will make a
        # <div> in the HTML and automaticall update it when the .text field is
        # updated in this python code. But if you want to insert a wtext in the
        # middle of a field, the following first attempt won't work:
        #     scene.append_to_caption('<table>')
        #     vpython.wtext(text='widget text')
        #     scene.append_to_caption('</table>')
        # because adding the wtext will also close the <table> tag.
        # But you can't make a wtext that contains HTML DOM tags either,
        # because every time the text changes several times a second, any open
        # dropdown menus will be closed.
        # So we have to insert a <div> where vpython expects it, manually.
        # We take advantage of the fact that manually modifying scene.caption
        # will remove the <div> that represents a wtext. Then we add the <div>
        # back, along with the id="x" that identifies the div, used by vpython.
        #
        # TL;DR the div_id variable is a bit magic, if you make a new wtext
        # before this, increment div_id by one..

        # self._scene.caption += "<table>\n"
        self._update_RTH(gui)
        gui.concat_caption("<table>\n")
        div_id = 1
        for caption, text_gen_func, helptext, new_section in [
            ("Orbit speed",
             lambda: f"{calc.orb_speed(self.reference):,.7g} m/s",
             "Speed required for circular orbit at current altitude",
             False),
            ("Periapsis",
             lambda: f"{calc.periapsis(self.reference):,.7g} m",
             "Lowest altitude in naïve orbit around reference",
             False),
            ("Apoapsis",
             lambda: f"{calc.apoapsis(self.reference):,.7g} m",
             "Highest altitude in naïve orbit around reference",
             False),
            ("HRT phase angle &nbsp",
             lambda: f"{round(np.degrees(self.habitat.heading))} degrees",
             "Current angle of habitat",
             False),
            ("Fuel: ",
             lambda: f"{abs(round(self.habitat.fuel, 1))} kg",
             "Remaining fuel of habitat",
             False),
            ("Throttle",
             lambda:
             f"{self.habitat.throttle:.1%}",
             "Percentage of habitat's maximum rated engines",
             False),

            ("Ref alt",
             lambda: f"{calc.altitude(self.reference, self.habitat):,.7g} m",
             "Altitude of habitat above reference surface",
             False),
            ("Ref speed",
             lambda: f"{calc.speed(self.reference, self.habitat):,.7g} m/s",
             "Speed of habitat above reference surface",
             False),
            ("Vertical speed",
             lambda:
             f"{calc.v_speed(self.reference, self.habitat):,.7g} m/s ",
             "Vertical speed of habitat towards/away reference surface",
             False),
            ("Horizontal speed",
             lambda:
             f"{calc.h_speed(self.reference, self.habitat):,.7g} m/s ",
             "Horizontal speed of habitat across reference surface",
             False),
            ("Targ alt",
             lambda:
             f"{calc.altitude(self.target, self.habitat):,.7g} m",
             "Altitude of habitat above reference surface",
             False),
            ("Targ speed",
             lambda:
             f"{calc.speed(self.target, self.habitat):,.7g} m/s",
             "Altitude of habitat above reference surface",
             False)

            # Pitch: ? degrees

            # Landing acceleration: ? m/s/s
        ]:
            gui.append_wtexts(vpython.wtext(text=text_gen_func()))
            gui.set_wtexts_text_func_at(-1, text_gen_func)
            gui.concat_caption(f"""<tr>
                <td {"class='newsection'" if new_section else ""}>
                    {caption}
                </td >
                <td class = "num{" newsection" if new_section else ""}" >
                    <div id = "{div_id}" >
                        {gui.wtexts_at(-1).text}
                </div >
                <div class = "helptext{"newsection" if new_section else ""}" 
                    style="font-size: 12px">
                        {helptext}
                </div >
                </td >
                </tr >\n""")

            div_id += 1
            self._update_RTH(gui)
        # end of for
        gui.concat_caption("</table>")
        self._set_menus(gui)
        gui.append_caption(style.HELP_CHECKBOX)
        gui.append_caption(" Help text")
        gui.append_caption(style.INPUT_CHEATSHEET)

        gui.append_caption(style.VPYTHON_CSS)
        gui.append_caption(style.VPYTHON_JS)
    # end of _set_caption

    def _set_menus(self, gui) -> None:
        """This creates dropped down menu which is used when set_caption."""

        def build_menu(*, choices: List[str] = None, bind: Callable = None,
                       selected: str = None, caption: str = None,
                       helptext: str = None) -> vpython.menu:

            menu = vpython.menu(
                choices=choices,
                pos=gui.get_cpation_anchor(),
                bind=bind,
                selected=selected)
            gui.append_caption(f"&nbsp;<b>{caption}</b>&nbsp;")
            gui.append_caption(
                f"<span class='helptext'>{helptext}</span>")
            gui.append_caption("\n")
            return menu
        # end of build_menu

        gui.set_centre_menu(build_menu(
            choices=list(gui.get_spheres()),
            bind=gui._recentre_dropdown_hook,
            selected=DEFAULT_CENTRE,
            caption="Centre",
            helptext="\nFocus of camera"
        ))

        build_menu(
            choices=list(gui.get_spheres()),
            bind=lambda selection: gui._set_reference(selection.selected),
            selected=DEFAULT_REFERENCE,
            caption="Reference",
            helptext=(
                "\nTake position, velocity relative to this.")
        )

        build_menu(
            choices=list(gui.get_spheres()),
            bind=lambda selection: gui._set_target(selection.selected),
            selected=DEFAULT_TARGET,
            caption="Target",
            helptext="\nFor use by NAV mode"
        )

        build_menu(
            choices=['deprt ref'],
            bind=lambda selection: self._set_navmode(selection.selected),
            selected='deprt ref',
            caption="NAV mode",
            helptext="\nAutomatically points habitat"
        )

        gui.set_time_acc_menu(build_menu(
            choices=[f'{n:,}×' for n in
                     [1, 5, 10, 50, 100, 1_000, 10_000, 100_000]],
            bind=gui._time_acc_dropdown_hook,
            selected=1,
            caption="Warp",
            helptext="\nSpeed of simulation"
        ))

        gui.append_caption("\n")
        vpython.checkbox(
            bind=gui._trail_checkbox_hook, checked=False, text='Trails')
        gui.append_caption(
            " <span class='helptext'>Graphically intensive</span>")
    # end of _set_menus

# end of class Menu